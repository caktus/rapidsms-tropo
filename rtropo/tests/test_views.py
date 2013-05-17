import json
import logging

import mock

from django.core import signing
from django.core.urlresolvers import reverse

from .utils import TropoTest, BACKEND_NAME


logger = logging.getLogger(__name__)


class TropoViewTest(TropoTest):

    disable_phases = True

    def send_to_view(self, data):
        """Send data to the tropo view, return whatever the response is"""
        encoded_data = json.dumps(data)
        url = reverse('tropo-backend')
        return self.client.post(
            url,
            encoded_data,
            content_type="application/json"
        )

    def test_cannot_get(self):
        # GET is not a valid method
        response = self.client.get(reverse('tropo-backend'))
        self.assertEqual(405, response.status_code)

    def test_invalid_response(self):
        """HTTP 400 should return if data is invalid."""
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self.send_to_view(data)
        self.assertEqual(response.status_code, 400)

    def test_incoming_message(self):
        # If we call the view as if Tropo is delivering a message, the
        # message is passed to RapidSMS. Any unicode is preserved.
        text = u"TEXT MESSAGE \u0123\u4321"
        data = {
            'session': {
                'from': {
                    'id': 'FROM',
                },
                'initialText': text,
                'token': self.router.backends[BACKEND_NAME].token,
            }
        }
        conn = mock.Mock()
        with mock.patch('rtropo.views.lookup_connections') as \
                lookup_connections:
            lookup_connections.return_value = [conn]
            with mock.patch('rtropo.views.receive') as receive:
                response = self.send_to_view(data)
        self.assertEqual(200, response.status_code, response.content)
        receive.assert_called()
        args, kwargs = receive.call_args
        received_text, connection = args
        self.assertEqual(text, received_text)
        self.assertEqual(conn, connection)
        response_program = json.loads(response.content)
        expected_program = {"tropo": [{"hangup": {}}]}
        self.assertEqual(expected_program, response_program)

    def test_view_execute(self):
        # If we call the view as if Tropo is passing the signed program,
        # we pass back the program as the response.  Any unicode is
        # preserved.
        program = {
            'tropo': [{'one': 1, 'two': u"Unicode \u0123\u4321"}]
        }
        signed_program = signing.dumps(program)
        data = {
            'session': {
                'parameters': {
                    'program': signed_program,
                },
                'token': self.get_config()['messaging_token'],
            }
        }
        response = self.send_to_view(data)
        self.assertEqual(200, response.status_code, response.content)
        expected_json = json.dumps(program)
        self.assertEqual(expected_json, response.content)

    def test_modified_program(self):
        # If the signed program's signature does not check out, we
        # fail the request and do not pass the program to Tropo (or
        # whoever it was who called us)
        program = [{'one': 1, 'two': 2}]
        signed_program = signing.dumps(program)
        bad_signed_program = signed_program + "BADSTUFF"
        data = {
            'session': {
                'parameters': {
                    'program': bad_signed_program,
                },
                'token': self.get_config()['messaging_token'],
            }
        }
        response = self.send_to_view(data)
        self.assertEqual(400, response.status_code, response.content)
        self.assertEqual("", response.content)
