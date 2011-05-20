# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import json
import logging

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from threadless_router.base import incoming
from tropo import Tropo

logger = logging.getLogger('rtropo.views')
logger.setLevel(logging.DEBUG)

"""
Info in cache:

{randomUUID} -> callback function
{randomUUID}_data -> callback data

request parameter 'callback_id' -> {randomUUID}

when we get a session ID:
  {session_ID}_callback -> callback function
  {session_ID}_data -> callback data
  delete {randomUUID} and {randomUUID}_data
"""


@csrf_exempt
def message_received(request, backend_name):
    """Handle HTTP requests from Tropo.
    """

    logger.debug("@@Got request from Tropo: %s" % request)

    if request.method == 'POST':
        logger.debug("@@%s" % request.raw_post_data)
        post = json.loads(request.raw_post_data)
        logger.debug("@@%r" % post)

        if 'result' in post:
            session_id = post['result']['sessionId']
        elif 'session' in post:
            session_id = post['session']['id']
        else:
            logger.error("@@HEY, post is neither result nor session, what's going on?")
            return HttpResponseServerError()
            
        # Do we need to pass this to somebody else?
        callback = cache.get("%s_callback" % session_id)
        if callback is not None:
            data = cache.get("%s_data" % session_id)
            return callback(request,data)

        if 'result' in post:
            logger.debug("@@ results?  we don't expect results, only callback users ought to be getting results.  Return error.")
            return HttpResponseServerError()

        s = post['session']

        if 'parameters' in s:
            parms      = s['parameters']
            
            if 'callback_id' in parms:
                logger.debug("@@callback_id found")
                callback = cache.get(parms['callback_id'])
                if callback is not None:
                    # first time we've been called for this callback
                    # move the cached data to be keyed by session ID
                    # so we can find it again
                    data = cache.get("%s_data" % parms['callback_id'])
                    cache.set("%s_callback" % session_id, callback)
                    cache.set("%s_data" % session_id, data)
                    cache.delete(parms['callback_id'])
                    cache.delete("%s_data" % parms['callback_id'])

                    logger.debug("@@Passing request to callback...")
                    return callback(request,data)
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
        # Not a post, so Tropo is just asking for our script
        # Give it to them
        # The code in outgoing.py assumes this script
        #return HttpResponse("""
#message(msg, { "to": numberToDial,  "network":"SMS", "callerID": callerID})
#log("Sent to %s: %s" % (numberToDial, msg))
#""")
