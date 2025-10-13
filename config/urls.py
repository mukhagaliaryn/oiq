from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.main.urls')),
    path('learn/', include('apps.learner.urls')),
]


urlpatterns += [re_path(r'^i18n/', include('django.conf.urls.i18n'))]
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += [re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})]
if settings.DEBUG:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]
