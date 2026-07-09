from core.utils.files import delete_old_file


def on_user_pre_save(sender, instance, **kwargs):
    delete_old_file(sender, instance, 'avatar')
