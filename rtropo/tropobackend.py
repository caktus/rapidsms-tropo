#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.backends.http import RapidHttpBacked
from django.http import HttpResponse, HttpResponseBadRequest
import datetime
from urllib import urlencode
from urllib2 import urlopen
from tropo import Tropo, Session

class TropoBackend(RapidHttpBacked):
    """ A RapidSMS backend for Tropo SMS API """

    def configure(self, config=None, **kwargs):
        self.config = config
        super(TropoBackend, self).configure(**kwargs)

    def handle_request(self, request):
	if request.method != 'POST':
		return HttpResponse('Not a post!')
        self.debug('This is the tropo Request (raw): %s' % request.raw_post_data)
	s = Session(request.raw_post_data)
	if not s.callId:
                t = Tropo()
                t.message(s.parameters['msg'], to="tel:+%s" %  s.parameters['numberToDial'], network="SMS")
                return HttpResponse(t.RenderJson())
	else:
	        message = self.message(request.POST)
        	if message:
            		self.route(message)

	        t = Tropo()
        	t.hangup()
	        return HttpResponse(t.RenderJson())


    def message(self, data):
        sms = data.get('msg', '')
        sender = data.get('user', '')
        if not sms or not sender:
            self.error('Missing from or text: %s' % data)
            return None
        now = datetime.datetime.utcnow()
        return super(TropoBackend, self).message(sender, sms, now)

    def send(self, message):
	base_url = 'http://api.tropo.com/1.0/sessions'
#	token = '1c58694261c3714c9598abaa13d22bdc9c859f31383805bb8445a3fe40e0e19d3017b06ed4e56ae582695210'		# Insert your token here
	token = '8dedf13d8330b24dade023972bf72db1eb347eefbcbf46aea81ea94a794385eeba9951d94debd9918b5f61b3'
	action = 'create'
	number = '14122677933'	

	params = urlencode([('action', action), ('token', token), ('numberToDial', message.connection.identity), ('msg', message.text)])
	self.debug("%s?%s" % (base_url, params))
	data = urlopen('%s?%s' % (base_url, params)).read()
        self.debug(data)

