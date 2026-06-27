from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.db.models.signals import pre_save
        from core.models import User, Subject
        from core.signals import on_user_pre_save, on_subject_pre_save

        pre_save.connect(on_user_pre_save, sender=User)
        pre_save.connect(on_subject_pre_save, sender=Subject)
