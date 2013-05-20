from django.conf import settings

from rapidsms.tests.harness import RapidTest


BACKEND_NAME = 'tropobackend'


class TropoTest(RapidTest):
    # Override TestRouter's override of the backends
    backends = settings.INSTALLED_BACKENDS

    def get_config(self):
        return settings.INSTALLED_BACKENDS[BACKEND_NAME]['config']
