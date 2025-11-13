from django.db.models.signals import post_save
from django.dispatch import receiver
from core.generics.models import User, Learner, Teacher, Manager


# Create user role
# ----------------------------------------------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_user_role(sender, instance, created, **kwargs):
    if created:
        if instance.user_role == 'learner':
            Learner.objects.create(user=instance)
        elif instance.user_role == 'teacher':
            Teacher.objects.create(user=instance)
        elif instance.user_role == 'manager':
            Manager.objects.create(user=instance)
