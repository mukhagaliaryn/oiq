from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GenericsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.generics'
    verbose_name = _('Generics models')


    def ready(self):
        import core.utils.signals
