from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        from django.db.models.signals import pre_save
        from apps.accounts.models import User
        from apps.accounts.signals import on_user_pre_save

        pre_save.connect(on_user_pre_save, sender=User)
