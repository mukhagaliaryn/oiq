from apps.accounts.models import Teacher


def get_teacher(user):
    return Teacher.objects.filter(user=user).select_related('user').first()
