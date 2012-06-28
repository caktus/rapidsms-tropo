# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import json
import logging

from django.core.urlresolvers import resolve
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from threadless_router.base import incoming
from tropo import Tropo

logger = logging.getLogger('rtropo.views')

@csrf_exempt
def message_received(request, backend_name):
    """Handle HTTP requests from Tropo.
    """

    #logger.debug("@@Got request from Tropo: %s" % request)

    if request.method == 'POST':
        logger.debug("@@ Raw data: %s" % request.raw_post_data)
        try:
            post = json.loads(request.raw_post_data)
        except Exception, e:
            logger.exception(e)
            logger.debug("EXCEPTION decoding post data")
            return HttpResponseServerError()
        logger.debug("@@ Decoded data: %r" % post)

        if 'result' in post:
            session_id = post['result']['sessionId']
        elif 'session' in post:
            session_id = post['session']['id']
        else:
            logger.error("@@HEY, post is neither result nor session, what's going on?")
            return HttpResponseServerError()
            
        # Do we need to pass this to somebody else?
        if 'result' in post:
            logger.debug("@@ results?  we don't expect results, only callback users ought to be getting results.  Return error.")
            return HttpResponseServerError()

        s = post['session']

        if 'parameters' in s:
            parms      = s['parameters']
            logger.debug("@@ got session")

            if 'callback_url' in parms:
                url = parms['callback_url']
                view, args, kwargs = resolve(url)
                kwargs['request'] = request
                logger.debug("@@ passing tropo request to %s" % url)
                try:
                    return view(*args, **kwargs)
                except Exception, e:
                    logger.error("@@Caught exception calling callback:")
                    logger.exception(e)
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
            logger.debug("@@responding to tropo with hangup")
            return HttpResponse(t.RenderJson())
        except Exception, e:
            logger.exception(e)
            logger.debug("@@responding to tropo with error")
            return HttpResponseServerError()
    else:
        # What?  We don't expect any GET to our URL because
        # our Tropo app should be a Web API app.
        logger.error("@@Unexpected GET to tropo URL")
        return HttpResponseServerError()
