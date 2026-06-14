from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/ckeditor/', include('core.urls')),
    path('admin/', admin.site.urls),

    # apps...
    path('', include('apps.main.urls')),
    path('learner/', include('apps.dashboard.learner.urls')),
    path('teacher/', include('apps.dashboard.teacher.urls')),

    prefix_default_language=True,
)


urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += [re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})]
if settings.DEBUG:
    urlpatterns += [
        path('__reload__', include('django_browser_reload.urls')),
    ]
