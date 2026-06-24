import hashlib

from PIL import Image, UnidentifiedImageError
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from core.models import FormatVariant, School
from core.utils.files import ckeditor_image_upload_path

MAX_UPLOAD_SIZE = 5 * 1024 * 1024


@staff_member_required
@csrf_protect
@require_POST
def ckeditor_image_upload(request):
    upload = request.FILES.get('upload')

    if upload is None:
        return JsonResponse({'error': {'message': _('File not found.')}}, status=400)

    if upload.size > MAX_UPLOAD_SIZE:
        return JsonResponse({'error': {'message': _('File size must not exceed 5MB.')}}, status=400)

    try:
        Image.open(upload).verify()
    except (UnidentifiedImageError, OSError):
        return JsonResponse({'error': {'message': _('Please upload a valid image file.')}}, status=400)

    upload.seek(0)
    file_hash = hashlib.sha256(upload.read()).hexdigest()
    upload.seek(0)

    path = ckeditor_image_upload_path(upload.name, file_hash)

    if not default_storage.exists(path):
        default_storage.save(path, upload)

    return JsonResponse({'url': default_storage.url(path)})


@staff_member_required
def format_variants(request):
    variants = FormatVariant.objects.filter(
        format_id=request.GET.get('format')
    ).values('id', 'name')

    return JsonResponse({'results': list(variants)})


# -------------- school field (HTMX) --------------
def school_field_view(request):
    city_id = request.GET.get('city')
    schools = (
        School.objects.filter(city_id=city_id, is_active=True).order_by('name')
        if city_id else School.objects.none()
    )

    class _SchoolForm(forms.Form):
        school = forms.ModelChoiceField(queryset=schools, required=True, empty_label=_('Select school'))

    form = _SchoolForm(initial={'school': request.GET.get('school')})
    return render(request, 'components/_school_field.html', {'field': form['school']})
