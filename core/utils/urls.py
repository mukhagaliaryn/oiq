from django.conf import settings
from django.urls import reverse


def build_absolute_url(host, viewname, *, urlconf=None, args=None, kwargs=None):
    """
    Хостаралық сілтеме (мыс. oiq.kz-тен school.oiq.kz-ке): reverse() тек ағымдағы
    request.urlconf ішінде жұмыс істейді, сондықтан мақсатты хосттың urlconf-ын
    анық көрсету керек. host — мыс. settings.BASE_DOMAIN немесе settings.SCHOOL_HOST.
    """
    scheme = 'http' if settings.DEBUG else 'https'
    port = ':8000' if settings.DEBUG else ''
    path = reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs)
    return f'{scheme}://{host}{port}{path}'
