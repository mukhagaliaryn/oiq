from apps.accounts.models import User


def get_active_students():
    return User.objects.filter(role=User.Role.LEARNER, is_active=True)
