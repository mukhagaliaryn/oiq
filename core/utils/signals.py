from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User


# Create user role
# ----------------------------------------------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_user_role(sender, instance, created, **kwargs):
    pass
