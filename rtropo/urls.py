from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',  # nopep8
    url(r"^(?P<backend_name>[\w-]+)/$", views.message_received,
        name='tropo'),
)
