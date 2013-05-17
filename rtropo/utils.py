from rapidsms.router import get_router

try:
    from rapidsms.router.base import BaseRouter
except ImportError:
    from rapidsms.router.blocking.router import BlockingRouter as BaseRouter


def get_backend(backend_name):

    router = get_router()

    # Older RapidSMS have get_router() return the class, not an instance
    if not isinstance(router, BaseRouter):
        router = router()

    backends = router.backends
    if backend_name in backends:
        return backends[backend_name]
    raise Exception("Backend `%s` not found in %r" % (backend_name, backends))
