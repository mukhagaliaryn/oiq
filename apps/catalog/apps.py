from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'apps.catalog'

    def ready(self):
        from django.db.models.signals import pre_save
        from apps.catalog.models import Subject
        from apps.catalog.signals import on_subject_pre_save

        pre_save.connect(on_subject_pre_save, sender=Subject)
