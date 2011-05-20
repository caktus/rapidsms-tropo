from urllib import urlencode
from urllib2 import urlopen

from rapidsms.backends.base import BackendBase

base_url = 'http://api.tropo.com/1.0/sessions'

class TropoBackend(BackendBase):
    """A RapidSMS threadless backend for Tropo"""

    def configure(self, config=None, **kwargs):
        self.config = config
        
    def start(self):
        """Override BackendBase.start(), which never returns"""
        self._running = True

    def send(self, message):
        self.debug("send(%s,%s)" % (message.connection.identity,message.text))
        token = self.config['messaging_token']
        action = 'create'
        # Tropo doesn't like dashes in phone numbers
        callerID = self.config['number'].replace("-","")
        numberToDial = message.connection.identity.replace("-","")

        params = urlencode([('action', action), ('token', token), ('numberToDial', numberToDial), ('msg', message.text), ('callerID', callerID)])
        self.debug("%s?%s" % (base_url, params))
        data = urlopen('%s?%s' % (base_url, params)).read()
        self.debug(data)
        return True

    def call_tropo(self,callback_url,message_type='text'):
        """Other apps can call this and pass a function.  
        We'll ask tropo to kick off our application and return.
        Soon, Tropo will POST to us.  When we get the post, we'll pass it to the function
        we were originally given to handle, which it should do by parsing the JSON it
        was POSTed and responding with some more JSON.  (See the Tropo WebAPI docs.)

        The callback_url is a URL.  When Tropo calls us back,
        we'll pass the request to whatever view django would normally
        use for that URL.  It can include parameters
        (e.g. "/patient/callback/1").  An easy way to build this is
        to use reverse:

          url = reverse('patient-callback', kwargs={ 'patient_id': patient_id })

        message_type is optional, or pass 'voice' to use the voice token instead of text.

        (We do this by adding some parms to the call we make to Tropo and looking for
        them on the return post.)
        """

        if message_type == 'text':
            token = self.config['messaging_token']
        else:
            token = self.config['voice_token']

        # Call Tropo
        parms = urlencode([('action','create'),
                           ('callback_url',callback_url),
                           ('token', token),
                           ])
        urlopen("%s?%s" % (base_url, parms)).read()
