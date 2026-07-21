from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SchoolConfig(AppConfig):
    name = 'apps.school'
    verbose_name = _('School system')
