from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

BASIC_INFO_FIELDS = ('first_name', 'last_name', 'middle_name', 'phone')
TEACHER_PROFILE_FIELDS = ('city', 'school')


# -------------- update_basic_info --------------
def update_basic_info(user, **fields):
    update_fields = [field for field in fields if field in BASIC_INFO_FIELDS]

    for field in update_fields:
        setattr(user, field, fields[field])

    if update_fields:
        user.save(update_fields=update_fields)

    return user


# -------------- update_teacher_profile --------------
def update_teacher_profile(teacher, subjects=None, **fields):
    update_fields = [field for field in fields if field in TEACHER_PROFILE_FIELDS]

    for field in update_fields:
        setattr(teacher, field, fields[field])

    if update_fields:
        teacher.save(update_fields=update_fields)

    if subjects is not None:
        teacher.subjects.set(subjects)

    return teacher


# -------------- set_avatar --------------
def set_avatar(user, file):
    user.avatar = file
    user.save(update_fields=['avatar'])

    return user


# -------------- remove_avatar --------------
def remove_avatar(user):
    if user.avatar:
        user.avatar.delete(save=False)
        user.save(update_fields=['avatar'])

    return user


# -------------- update_email --------------
def update_email(user, email):
    email = email.lower().strip()

    if User.objects.filter(email=email).exclude(pk=user.pk).exists():
        raise ValidationError(_('This email is already in use.'))

    user.email = email
    user.save(update_fields=['email'])

    return user


# -------------- change_password --------------
def change_password(user, current_password, new_password):
    if not user.check_password(current_password):
        raise ValidationError(_('Current password is incorrect.'))

    validate_password(new_password, user=user)

    user.set_password(new_password)
    user.save(update_fields=['password'])

    return user


# -------------- deactivate_account --------------
def deactivate_account(user):
    user.is_active = False
    user.save(update_fields=['is_active'])

    return user
