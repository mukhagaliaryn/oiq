import hashlib

from PIL import Image, UnidentifiedImageError
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

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
