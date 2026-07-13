from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, re_path, include
from django.views.static import serve


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # landing (org таңдау/онбординг) '' -де, workspace '<org>/'-де — екеуі бір app_name='school'
    # пакетінде біріктірілген (config/urls_main.py-дегі accounts секілді, reverse() gotcha-сын болдырмау үшін).
    path('', include('apps.school.urls')),
    prefix_default_language=True,
)

urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += [re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})]
if settings.DEBUG:
    urlpatterns += [
        path('__reload__', include('django_browser_reload.urls')),
    ]
