from django.conf.urls import patterns, url

from ..views import message_received
from .utils import BACKEND_NAME


urlpatterns = patterns('',  # nopep8
    url(r"^backend_tropo/$", name="tropo-backend",
        view=message_received,
        kwargs={'backend_name': BACKEND_NAME}),

    # Dummies
    url(r"^rapidsms-login", name="rapidsms-login", view=message_received),
)
