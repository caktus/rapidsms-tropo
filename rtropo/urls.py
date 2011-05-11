from django.conf.urls.defaults import *

from rtropo import views

urlpatterns = patterns('',
    url(r"^(?P<backend_name>[\w-]+)/$", views.message_received,
        name='tropo'),
)
