rapidsms-tropo
============================

Basic `Tropo <http://www.tropo.com>`_ backend for the `RapidSMS <http://www.rapidsms.org/>`_ `Threadless router <https://github.com/caktus/rapidsms-threadless-router>`_

Requirements
------------

 * `rapidsms-threadless-router <https://github.com/caktus/rapidsms-threadless-router>`_
 * `tropo-webapi-python <https://github.com/tropo/tropo-webapi-python>`_  (pip install tropo-webapi-python)

Usage
-----

Create an application at tropo.com.  Its type should be "Web API".

Add rtropo to your Python path and set up the Tropo backend in your Django settings file. For example::

    INSTALLED_BACKENDS = {
        "tropo": {
            "ENGINE": "rtropo.backend",
            'config': {
                # Your Tropo application's outbound token for messaging
                'messaging_token': 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
                # Your Tropo application's outbound token for voice (optional)
                'voice_token': 'ZZZZZZZZZZZZZZZZZZZZZZZZZZ',
                # Your Tropo application's voice/messaging phone number (including country code, which must be +1 because only US numbers can be used for messaging)
                'number': '+1-###-###-####',
            }
        },
    }

At this point you should be able to send outgoing messages, but more setup is needed to receiving incoming messages.

Set up your URLconf to send incoming http requests from tropo to rtropo.views.message_received, passing the backend_name parameter.  For example::

    from django.conf.urls.defaults import *
    from rtropo import views

    urlpatterns = patterns('',
        url(r"^tropo/$", views.message_received, kwargs={'backend_name': 'tropo'}, name='tropo'),
    )

You can use any URL.

Configure your Tropo application at tropo.com so its SMS/Messaging URL will invoke the Django URL that you just configured.  E.g.::

    http://yourserver.example.com/tropo/

Voice and more complicated stuff
--------------------------------

The tropo backend provides a way for your app to get access to tropo
and do whatever it wants using Tropo's Web API.  See
rtropo/outgoing.py, TropoBackend.call_tropo().


Background
----------

 * `Tropo's API doc <https://www.tropo.com/docs/webapi/how_tropo_web_api_works.htm>`_
 * `tropo-webapi-python doc <https://github.com/tropo/tropo-webapi-python/blob/master/README>`_
 * `Receiving text messages <https://www.tropo.com/docs/scripting/receiving_text_messages.htm>`_

Development by `Caktus Consulting Group <http://www.caktusgroup.com/>`_.


Changelog
--------------------------------

v0.1.0 (Released 2012-06-28)
________________________________

- Initial stable release
