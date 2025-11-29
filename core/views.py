from django.http import JsonResponse
from core.models import QuestionVariant


# format variants api
# ----------------------------------------------------------------------------------------------------------------------
def get_variants(request):
    format_id = request.GET.get('format_id')

    if not format_id:
        return JsonResponse([], safe=False)
    variants = QuestionVariant.objects.filter(
        format_id=format_id
    ).values('id', 'name')

    return JsonResponse(list(variants), safe=False)
