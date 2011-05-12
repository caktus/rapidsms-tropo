# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from threadless_router.base import incoming
from tropo import Tropo, Session

@csrf_exempt
def message_received(request, backend_name):
    """Handle HTTP requests from Tropo.
    If POST, we've received a message; if GET, Tropo wants our script."""

    if request.method == 'POST':
        # somebody called our Tropo number
        # parse the data
        s = Session(request.raw_post_data)
        from_address = s.dict['from']['id']
        text = s.dict['initialText']

        logging.debug("Received message from %s: %s" % (from_address, text))

        # pass the message to RapidSMS
        incoming(backend_name, from_address, text)

        # Respond nicely to Tropo
        t = Tropo()
        t.hangup()
        return HttpResponse(t.RenderJson())
    else:
        # Not a post, so Tropo is just asking for our script
        # Give it to them
        # The code in outgoing.py assumes this script
        return HttpResponse("""
message(msg, { "to": numberToDial,  "network":"SMS", "callerID": callerID})
log("Sent to %s: %s" % (numberToDial, msg))
""")
