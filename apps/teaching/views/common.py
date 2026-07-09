from django.http import Http404
from apps.catalog.selectors import get_subject


def owned_subject(request, pk):
    teacher = request.user.teacher
    subject = get_subject(pk)

    if subject.pk != teacher.subject_id:
        raise Http404

    return subject
