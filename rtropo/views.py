# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import json
import logging

from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from threadless_router.base import incoming
from tropo import Tropo

logger = logging.getLogger('rtropo.views')

@csrf_exempt
def message_received(request, backend_name):
    """Handle HTTP requests from Tropo.
    """

    if request.method == 'POST':
        logger.debug("@@%s" % request.raw_post_data)
        post = json.loads(request.raw_post_data)
        logger.debug("@@%r" % post)

        if 'result' in post:
            # FIXME: Results of something - not sure yet what to do with this
            session_id = post['result']['sessionId']
            logger.debug("@@not sure yet what to do with a result")
            return HttpResponse('')

        if 'session' not in post:
            logger.error("@@HEY, post is neither result nor session, what's going on?")
            return HttpResponseServerError()

        s = post['session']
        session_id = s['id']

        if 'parameters' in s:
            parms      = s['parameters']

            # Do we need to pass this to somebody else?
            if 'callback_id' in parms:
                logger.debug("@@callback_id found")
                from django.core.cache import cache
                callback = cache.get(parms['callback_id'])
                if callback is not None:
                    return callback(request)
                logger.error("@@Could not find function for callback id %s" % parms['callback_id'])
                return HttpResponseServerError()

            # Did we call Tropo so we could send a text message?
            if 'numberToDial' in parms:
                # Construct a JSON response telling Tropo to do that
                logger.debug("@@Telling Tropo to send message")
                try:
                    j = json.dumps({ "tropo": [{ 'message': {
                        'say': { 'value': parms['msg'] },
                        'to':  parms['numberToDial'],
                        'from': parms['callerID'],
                        'channel': 'TEXT',
                        'network': 'SMS' }},]})
                    logger.debug("@@%s" % j)
                    return HttpResponse(j)
                except Exception, e:
                    logger.exception(e)
                    return HttpResponseServerError()

        # Must have received a message
        logger.debug("@@Got a text message")
        try:
            from_address = s['from']['id']
            text = s['initialText']

            logger.debug("@@Received message from %s: %s" % (from_address, text))

            # pass the message to RapidSMS
            incoming(backend_name, from_address, text)

            # Respond nicely to Tropo
            t = Tropo()
            t.hangup()
            return HttpResponse(t.RenderJson())
        except Exception, e:
            logger.exception(e)
            return HttpResponseServerError()
    else:
        # What?  We don't expect any GET to our URL because
        # our Tropo app should be a Web API app.
        logger.error("@@Unexpected GET to tropo URL")
        return HttpResponseServerError()
        # Not a post, so Tropo is just asking for our script
        # Give it to them
        # The code in outgoing.py assumes this script
        return HttpResponse("""
message(msg, { "to": numberToDial,  "network":"SMS", "callerID": callerID})
log("Sent to %s: %s" % (numberToDial, msg))
""")
