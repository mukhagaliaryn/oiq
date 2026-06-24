from django.shortcuts import get_object_or_404

from core.models import Subject


def owned_subject(request, pk):
    teacher = request.user.teacher
    return get_object_or_404(
        Subject.objects.filter(pk=teacher.subject_id, is_active=True),
        pk=pk,
    )
