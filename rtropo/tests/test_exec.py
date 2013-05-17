# Tests for execute_tropo_program
import json

from django.core import signing

import mock

from .utils import TropoTest, BACKEND_NAME


class TestExecute(TropoTest):

    def test_execute(self):
        # The execute_program method on the backend passes the signed
        # program to post. Any unicode is preserved too.
        program = [{'one': 1, 'two': u"Unicode \u0123\u4321"}]

        result = {
            'success': True,
        }
        mock_response = mock.Mock(status_code=200, content=json.dumps(result))
        with mock.patch('requests.post') as post:
            post.return_value = mock_response
            self.router.backends[BACKEND_NAME].execute_tropo_program(program)
        post.assert_called()
        args, kwargs = post.call_args
        data = json.loads(kwargs['data'])
        signed_program = data['program']
        extracted_program = signing.loads(signed_program)
        self.assertEqual(program, extracted_program)
        self.assertEqual(self.get_config()['messaging_token'], data['token'])
