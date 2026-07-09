import uuid
from datetime import datetime
from pathlib import Path


def delete_old_file(sender, instance, field_name):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_file = getattr(old, field_name)
    old_name = getattr(old_file, 'name', None)
    new_name = getattr(getattr(instance, field_name), 'name', None)
    if old_name and old_name != new_name:
        old_file.storage.delete(old_name)


def user_avatar_upload_path(instance, filename):
    extension = Path(filename).suffix

    filename = f'{uuid.uuid4().hex}{extension}'

    return (
        f'core/users/avatars/'
        f'{datetime.now().strftime("%Y/%m")}/'
        f'{filename}'
    )


def ckeditor_image_upload_path(filename, file_hash):
    extension = Path(filename).suffix

    return f'core/ckeditor/{file_hash}{extension}'


def question_import_image_path(batch_id, index, extension):
    return f'core/questions/imports/{batch_id}/{index}{extension}'
