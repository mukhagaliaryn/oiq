from apps.directory.models import Grade


def get_active_grades():
    return Grade.objects.filter(is_active=True)
