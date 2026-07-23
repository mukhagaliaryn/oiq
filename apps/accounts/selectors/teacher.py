from apps.accounts.models import Teacher


def get_teacher(user):
    return Teacher.objects.filter(user=user).select_related('user').first()


def get_teachers_by_ids(ids):
    return Teacher.objects.filter(pk__in=ids).select_related('user')
