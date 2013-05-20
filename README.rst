rapidsms-tropo
============================

Basic `Tropo <http://www.tropo.com>`_ backend for
`RapidSMS <http://www.rapidsms.org/>`_, version 0.14.0 or later.

Requirements
------------

 * `RapidSMS <http://www.rapidsms.org>`_, version 0.14.0 or later
    (pip install 'rapidsms>=0.14.0')
 * `Django <https://djangoproject.com>`_, version 1.4 or later.

Usage
-----

Create an application at tropo.com.  Its type should be "Web API".

Add rtropo to your Python path and set up the Tropo backend in your Django
settings file.

The required settings for your Tropo backend in INSTALLED_BACKENDS are:

ENGINE
    "rtropo.outgoing.TropoBackend"

config
    A dictionary with the rest of your settings for this backend. Required
    settings inside `config` are:

    messaging_token
        Your messaging token from Tropo (a long hex string)

    number
        The phone number your Tropo app is using. Must start with "+" and the
        country code.

For example::

    INSTALLED_BACKENDS = {
        "my-tropo-backend": {
            "ENGINE": "rtropo.outgoing.TropoBackend",
            'config': {
                # Your Tropo application's outbound token for messaging (required)
                'messaging_token': 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
                # Your Tropo application's voice/messaging phone number, starting
                # with "+" and the country code (required)
                'number': '+1-###-###-####',
            },
        },
    }

At this point you should be able to send outgoing messages, but more setup is needed to receiving incoming messages.

Set up your URLconf to send incoming http requests from tropo to
`rtropo.views.message_received`, passing the backend_name parameter, whose
value must be the same as the backend name you used in INSTALLED_BACKENDS.

For example::

    from django.conf.urls.defaults import *
    from rtropo import views

    urlpatterns = patterns('',
        url(r"^tropo/$",
            views.message_received,
            kwargs={'backend_name': 'my-tropo-backend'},
            name='tropo'),
    )

You can use any URL.  If you want to add some (slight) protection against
someone other than Tropo passing you messages pretending to be Tropo, you
might make your URL long and random, e.g.::

    from django.conf.urls.defaults import *
    from rtropo import views

    urlpatterns = patterns('',
        url(r"^534bd769-3e2e-42bd-8337-2099d9f38858/$",
            views.message_received,
            kwargs={'backend_name': 'my-tropo-backend'},
            name='tropo'),
    )

Configure your Tropo application at tropo.com so its SMS/Messaging URL will invoke the Django URL that you just configured.  E.g.::

    https://yourserver.example.com/534bd769-3e2e-42bd-8337-2099d9f38858/

Background
----------

 * `Tropo's API doc <https://www.tropo.com/docs/webapi/how_tropo_web_api_works.htm>`_
 * `Receiving text messages <https://www.tropo.com/docs/scripting/receiving_text_messages.htm>`_

Development by `Caktus Consulting Group <http://www.caktusgroup.com/>`_.

Changelog
--------------------------------

v0.2.0 (Released 2013-05-20)
________________________________

* Updates for RapidSMS 0.14 and later.
* Support for bulk messaging - with RapidSMS 0.14.0 or later, many messages
  can be sent without requiring separate round trip requests to Tropo for each.
* Add tests
* Add tox test runner
* Drop Tropo python library, which was hardly being used anyway.
* Security improvements.

v0.1.2 (Released 2013-05-17)
________________________________

- Add validation of some incoming requests from Tropo.
- Probably last version to support threadless-router, rapidsms<0.10.0

v0.1.1 (Released 2012-07-02)
________________________________

- Updated MANIFEST to include distribute_setup.py


v0.1.0 (Released 2012-06-28)
________________________________

- Initial stable release
