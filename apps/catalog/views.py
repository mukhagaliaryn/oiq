from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from apps.catalog.selectors import get_format_variants


@staff_member_required
def format_variants(request):
    variants = get_format_variants(request.GET.get('format')).values('id', 'name')
    return JsonResponse({'results': list(variants)})
