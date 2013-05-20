#!/usr/bin/env python
import sys

from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'rapidsms',
            'rtropo',
        ),
        SITE_ID=1,
        SECRET_KEY='super-secret',
        ROOT_URLCONF='rtropo.tests.urls',
        INSTALLED_BACKENDS={
            'tropobackend': {
                'ENGINE': 'rtropo.outgoing.TropoBackend',
                'config': {
                    "messaging_token": "12345abc",
                    "number": "+12345",
                },
            }
        }
    )


# Note: We cannot import this until after the settings are configured,
# or Django throws a fit
from django.test.utils import get_runner


def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    if 'test' in sys.argv[1:]:
        sys.argv.remove('test')
    args = sys.argv[1:] or ['rtropo', ]
    failures = test_runner.run_tests(args)
    sys.exit(failures)


if __name__ == '__main__':
    import logging

    root_logger = logging.getLogger('')
    # root_logger.setLevel(logging.DEBUG)
    # root_logger.addHandler(logging.StreamHandler())

    runtests()
