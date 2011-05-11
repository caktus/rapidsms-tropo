# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from threadless_router.base import incoming

from tropo import Tropo

def message_received(request, backend_name):

    if request.method != 'POST':
        return HttpResponse('Not a post!')
    self.debug('This is the tropo Request (raw): %s' % request.raw_post_data)
    text = request.POST.get('msg','')
    identity = request.POST.get('user','')
    if not text or not identity:
        self.error('Missing from or text: %s' % request.POST)
    else:
        incoming(backend_name, identity, text)

    t = Tropo()
    t.hangup()
    return HttpResponse(t.RenderJson())
