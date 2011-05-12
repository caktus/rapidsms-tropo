-*- restructuredtext -*-

rtropo
=======

Basic `Tropo <http://www.tropo.com>`_ backend for the `RapidSMS <http://www.rapidsms.org/>`_ `Threadless router <https://github.com/caktus/rapidsms-threadless-router>`_

Requirements
------------

 * `tropo-webapi-python <https://github.com/tropo/tropo-webapi-python>`_  (pip install tropo-webapi-python)

Usage
-----

Create an application at tropo.com.  Its type should be "Tropo scripting".

Upload the provided 'troposcript.py' as a 'Hosted File' (you'll probably have to rename it, but keep the .py extension) and make sure the application settings give the link to that script under 'What URL powers SMS/messaging calls to your app?'.

Add rtropo to your Python path and set up the Tropo backend in your Django settings file. For example::

    INSTALLED_BACKENDS = {
        "tropo": {
            "ENGINE": "rtropo.backend",
            'config': {
                # Your Tropo application's outbound token for messaging
                'messaging_token': 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
                # Your Tropo application's voice/messaging phone number (including country code, which must be +1 for US)
                'number': '+1-###-###-####',
                # SMS/messaging URL of your application
                #'script_url': 'http://hosting.tropo.com/69999/www/aremind2script.py',
            }
        },
    }

At this point you should be able to send outgoing messages, but more setup is needed to receiving incoming messages.

Set up your URLconf to send incoming http requests from tropo to rtropo.views.message_received, passing the backend_name parameter.  For example::

    from django.conf.urls.defaults import *
    from rtropo import views

    urlpatterns = patterns('',
        url(r"^(?P<backend_name>[\w-]+)/$", views.message_received,
            name='tropo'),
    )

or::

    from django.conf.urls.defaults import *
    from rtropo import views

    urlpatterns = patterns('',
        url(r"^sms/$", views.message_received,
            name='tropo',
            kwargs = { 'backend_name': 'tropo'}),
    )


Background
----------

 * `Tropo's API doc <https://www.tropo.com/docs/webapi/how_tropo_web_api_works.htm>`_
 * `tropo-webapi-python doc <https://github.com/tropo/tropo-webapi-python/blob/master/README>`_
 * `Receiving text messages <https://www.tropo.com/docs/scripting/receiving_text_messages.htm>`_

Development by `Caktus Consulting Group <http://www.caktusgroup.com/>`_.
