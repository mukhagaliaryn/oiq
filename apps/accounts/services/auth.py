from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from apps.accounts.models import Teacher

User = get_user_model()


# -------------- get_user_redirect_url --------------
def get_user_redirect_url(user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return reverse('admin:index')

    if user.role == User.Role.TEACHER:
        return reverse('teaching:dashboard')

    if user.role == User.Role.LEARNER:
        return reverse('learning:dashboard')

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
    user.role = User.Role.LEARNER
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
    user.role = User.Role.TEACHER
    user.is_active = False

    user.save()

    user.username = generate_username(
        email=user.email,
        user_id=user.id,
    )
    user.save(update_fields=['username'])

    Teacher.objects.create(
        user=user,
        city=form.cleaned_data.get('city'),
        school=form.cleaned_data.get('school'),
        subject=form.cleaned_data.get('subject'),
        agreement_accepted_at=agreement_accepted_at,
    )

    return user


# -------------- activate_user --------------
def activate_user(user):
    user.is_active = True
    user.save(update_fields=['is_active'])

    return user
