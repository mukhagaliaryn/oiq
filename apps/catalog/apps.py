from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogConfig(AppConfig):
    name = 'apps.catalog'
    verbose_name = _('Catalog')

    def ready(self):
        from django.db.models.signals import pre_save
        from apps.catalog.models import Subject
        from apps.catalog.signals import on_subject_pre_save

        pre_save.connect(on_subject_pre_save, sender=Subject)
