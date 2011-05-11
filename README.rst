-*- restructuredtext -*-

rtropo
=======

Basic `Tropo <http://www.tropo.com>`_ backend for the `RapidSMS <http://www.rapidsms.org/>`_ `Threadless router <https://github.com/caktus/rapidsms-threadless-router>`_

Requirements
------------

 * `tropo-webapi-python <https://github.com/tropo/tropo-webapi-python>`_  (pip install tropo-webapi-python)

Usage
-----

Add rtropo to your Python path and setup the Tropo backend in your Django settings file. For example::

    INSTALLED_BACKENDS = {
        "tropo": {
            "ENGINE": "rtropo.backend",
            'config': {
                'auth_token': 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
                'number': '(###) ###-####',
            }
        },
    }

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
