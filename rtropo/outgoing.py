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
        token = self.config['auth_token']
        action = 'create'
        number = self.config['number']

        params = urlencode([('action', action), ('token', token), ('numberToDial', message.connection.identity), ('msg', message.text)])
        self.debug("%s?%s" % (base_url, params))
        data = urlopen('%s?%s' % (base_url, params)).read()
        self.debug(data)
        return True
