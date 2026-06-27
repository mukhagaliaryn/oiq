def _delete_old_file(sender, instance, field_name):
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


def on_user_pre_save(sender, instance, **kwargs):
    _delete_old_file(sender, instance, 'avatar')


def on_subject_pre_save(sender, instance, **kwargs):
    _delete_old_file(sender, instance, 'cover')
