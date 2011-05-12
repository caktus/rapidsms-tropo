from urllib import urlencode
from urllib2 import urlopen

from rapidsms.backends.base import BackendBase

class TropoBackend(BackendBase):
    """A RapidSMS threadless backend for Tropo"""

    def configure(self, config=None, **kwargs):
        self.config = config
        
    def start(self):
        """Override BackendBase.start(), which never returns"""
        self._running = True

    def send(self, message):
        self.debug("send(%s)" % message)
        base_url = 'http://api.tropo.com/1.0/sessions'
        token = self.config['messaging_token']
        action = 'create'
        # Tropo doesn't like dashes in phone numbers
        callerID = self.config['number'].replace("-","")
        numberToDial = message.connection.identity.replace("-","")

        # This approach assumes that we are giving a particular script
        # to Tropo - see views.py for that script

        params = urlencode([('action', action), ('token', token), ('numberToDial', numberToDial), ('msg', message.text), ('callerID', callerID)])
        self.debug("%s?%s" % (base_url, params))
        data = urlopen('%s?%s' % (base_url, params)).read()
        self.debug(data)
        return True
