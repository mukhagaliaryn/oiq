from core.utils.files import delete_old_file


def on_subject_pre_save(sender, instance, **kwargs):
    delete_old_file(sender, instance, 'cover')
