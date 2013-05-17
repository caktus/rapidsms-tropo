# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import json
import logging

from django.core import signing
from django.http import HttpResponse, HttpResponseServerError, \
    HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


logger = logging.getLogger('rtropo.views')


from rapidsms.router import receive, lookup_connections


@require_POST
@csrf_exempt
def message_received(request, backend_name):
    """Handle HTTP requests from Tropo.
    """

    logger.debug("@@ request from Tropo - raw data: %s" % request.body)
    try:
        post = json.loads(request.body)
    except ValueError:
        logger.exception("EXCEPTION decoding post data in incoming request")
        return HttpResponseBadRequest()
    except Exception:
        logger.exception("@@responding to tropo with error")
        return HttpResponseServerError()
    logger.debug("@@ Decoded data: %r" % post)

    if 'session' not in post:
        logger.error("@@HEY, post does not contain session, "
                     "what's going on?")
        return HttpResponseBadRequest()

    session = post['session']
    parms = session.get('parameters', {})

    if 'program' in parms:
        # Execute a program that we passed to Tropo to pass back to us.
        # Extract the program, while verifying it came from us and
        # has not been modified.
        try:
            program = signing.loads(parms['program'])
        except signing.BadSignature:
            logger.exception("@@ received program with bad signature")
            return HttpResponseBadRequest()

        return HttpResponse(json.dumps(program))

    if 'from' in session:
        # Must have received a message
        # FIXME: is there any way we can verify it's really Tropo calling us?
        logger.debug("@@Got a text message")
        try:
            from_address = session['from']['id']
            text = session['initialText']

            logger.debug("@@Received message from %s: %s" %
                         (from_address, text))

            # pass the message to RapidSMS
            identity = from_address
            connections = lookup_connections(backend_name, [identity])
            receive(text, connections[0])

            # Respond nicely to Tropo
            program = json.dumps({"tropo": [{"hangup": {}}]})
            logger.debug("@@responding to tropo with hangup")
            return HttpResponse(program)
        except Exception:
            logger.exception("@@responding to tropo with error")
            return HttpResponseServerError()

    logger.error("@@No recognized command in request from Tropo")
    return HttpResponseBadRequest()
