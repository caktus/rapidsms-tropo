import json
import logging

from django.core.exceptions import ImproperlyConfigured
from django.core import signing

from rapidsms.backends.base import BackendBase

import requests


logger = logging.getLogger(__name__)

base_url = 'https://api.tropo.com/1.0/sessions'


class TropoBackend(BackendBase):
    """A RapidSMS backend for Tropo"""

    def configure(self, config=None, **kwargs):
        """
        We expect all of our config (apart from the ENGINE) to be
        in a dictionary called 'config' in our INSTALLED_BACKENDS entry
        """
        self.config = config or {}
        for key in ['messaging_token', 'number']:
            if key not in self.config:
                msg = "Tropo backend config must set '%s'; config is %r" %\
                      (key, config)
                raise ImproperlyConfigured(msg)
        if kwargs:
            msg = "All tropo backend config should be within the `config`"\
                "entry of the backend dictionary"
            raise ImproperlyConfigured(msg)

    @property
    def token(self):
        return self.config['messaging_token']

    def execute_tropo_program(self, program):
        """
        Ask Tropo to execute a program for us.

        We can't do this directly;
        we have to ask Tropo to call us back and then give Tropo the
        program in the response body to that request from Tropo.

        But we can pass data to Tropo and ask Tropo to pass it back
        to us when Tropo calls us back. So, we just bundle up the program
        and pass it to Tropo, then when Tropo calls us back, we
        give the program back to Tropo.

        We also cryptographically sign our program, so that
        we can verify when we're called back with a program, that it's
        one that we sent to Tropo and has not gotten mangled.

        See https://docs.djangoproject.com/en/1.4/topics/signing/ for more
        about the signing API.

        See https://www.tropo.com/docs/webapi/passing_in_parameters_text.htm
        for the format we're using to call Tropo, pass it data, and ask
        them to call us back.



        :param program: A Tropo program, i.e. a dictionary with a 'tropo'
            key whose value is a list of dictionaries, each representing
            a Tropo command.
        """
        # The signer will also "pickle" the data structure for us
        signed_program = signing.dumps(program)

        params = {
            'action': 'create',  # Required by Tropo
            'token': self.config['messaging_token'],  # Identify ourselves
            'program': signed_program,  # Additional data
        }
        data = json.dumps(params)

        # Tell Tropo we'd like our response in JSON format
        # and our data is in that format too.
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
        }
        response = requests.post(base_url,
                                 data=data,
                                 headers=headers)

        # If the HTTP request failed, raise an appropriate exception - e.g.
        # if our network (or Tropo) are down:
        response.raise_for_status()

        result = json.loads(response.content)
        if not result['success']:
            raise Exception("Tropo error: %s" % result.get('error', 'unknown'))

    def send(self, id_, text, identities, context=None):
        """
        Send messages when using RapidSMS 0.14.0 or later.

        We can send multiple messages in one Tropo program, so we do
        that.

        :param id_: Unused, included for compatibility with RapidSMS.
        :param string text: The message text to send.
        :param identities: A list of identities to send the message to
            (a list of strings)
        :param context: Unused, included for compatibility with RapidSMS.
        """

        # Build our program
        from_ = self.config['number'].replace('-', '')
        commands = []
        for identity in identities:
            # We'll include a 'message' command for each recipient.
            # The Tropo doc explicitly says that while passing a list
            # of destination numbers is not a syntax error, only the
            # first number on the list will get sent the message. So
            # we have to send each one as a separate `message` command.
            commands.append(
                {
                    'message': {
                        'say': {'value': text},
                        'to': identity,
                        'from': from_,
                        'channel': 'TEXT',
                        'network': 'SMS'
                    }
                }
            )
            program = {
                'tropo': commands,
            }
        self.execute_tropo_program(program)
