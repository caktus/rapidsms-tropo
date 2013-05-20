import mock

from .utils import TropoTest,  BACKEND_NAME


class TropoSendTest(TropoTest):

    def test_send(self):
        # send method passes a reasonable Tropo program to
        # execute_tropo_program
        backend = self.router.backends[BACKEND_NAME]
        config = self.get_config()
        FROM = config['number']
        text = u"MESSAGE\u0123\u0743"
        with mock.patch.object(backend, 'execute_tropo_program') as execute:
            backend.send(None, text, ["id1", "id2"])
        execute.assert_called()
        args, kwargs = execute.call_args
        program = args[0]
        expected_program = {
            'tropo': [
                {
                    'message': {
                        'say': {'value': text},
                        'to': "id1",
                        'from': FROM,
                        'channel': 'TEXT',
                        'network': 'SMS',
                    }
                },
                {
                    'message': {
                        'say': {'value': text},
                        'to': "id2",
                        'from': FROM,
                        'channel': 'TEXT',
                        'network': 'SMS',
                    }
                }
            ]
        }
        self.assertEqual(expected_program, program)
