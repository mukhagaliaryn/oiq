from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from apps.accounts.models import Teacher
from core.utils.urls import build_absolute_url

User = get_user_model()


# -------------- get_user_redirect_url --------------
def get_user_redirect_url(user):
    if user.is_superuser or user.account_type == User.AccountType.ADMIN:
        return reverse('admin:index')

    if user.account_type == User.AccountType.TEACHER:
        return reverse('teaching:dashboard')

    if user.account_type == User.AccountType.LEARNER:
        return reverse('learning:dashboard')

    if user.account_type == User.AccountType.SCHOOL_USER:
        return build_absolute_url(settings.SCHOOL_HOST, 'school:landing', urlconf='config.urls_school')

    return reverse('main:main')


# -------------- generate_username --------------
def generate_username(email, user_id=None):
    username = slugify(email.split('@')[0])

    if not username:
        username = 'user'

    if not User.objects.filter(username=username).exists():
        return username

    if user_id:
        return f'{username}_{user_id}'

    return username


# -------------- create_learner_user --------------
def create_learner_user(*, form):
    user = form.save(commit=False)

    user.email = form.cleaned_data['email'].lower()
    user.account_type = User.AccountType.LEARNER
    user.is_active = False

    user.save()

    user.username = generate_username(
        email=user.email,
        user_id=user.id,
    )
    user.save(update_fields=['username'])

    return user


# -------------- create_teacher_user --------------
def create_teacher_user(*, form, agreement_accepted_at=None):
    user = form.save(commit=False)

    user.email = form.cleaned_data['email'].lower()
    user.account_type = User.AccountType.TEACHER
    user.is_active = False

    user.save()

    user.username = generate_username(
        email=user.email,
        user_id=user.id,
    )
    user.save(update_fields=['username'])

    teacher = Teacher.objects.create(
        user=user,
        city=form.cleaned_data.get('city'),
        school=form.cleaned_data.get('school'),
        agreement_accepted_at=agreement_accepted_at,
    )
    teacher.subjects.set(form.cleaned_data.get('subjects') or [])

    return user


# -------------- create_external_user --------------
def create_external_user(*, email, first_name='', last_name='', account_type):
    """
    Сыртқы жүйе (мыс. school) арқылы қолданушыны тіркеу — тіркеу формасынсыз, дереу белсенді.
    Пароль кездейсоқ генерацияланады (MVP: "парольді орнату" email-і жоқ, кейін қосылады).
    """
    user = User.objects.create(
        email=email.lower(),
        first_name=first_name,
        last_name=last_name,
        account_type=account_type,
        is_active=True,
    )
    user.username = generate_username(email=user.email, user_id=user.id)
    user.set_password(get_random_string(32))
    user.save(update_fields=['username', 'password'])

    if account_type == User.AccountType.TEACHER:
        Teacher.objects.create(user=user)

    return user


# -------------- activate_user --------------
def activate_user(user):
    user.is_active = True
    user.save(update_fields=['is_active'])

    return user
