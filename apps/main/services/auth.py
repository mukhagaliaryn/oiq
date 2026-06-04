from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Teacher
User = get_user_model()


def get_user_redirect_url(user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return reverse('admin:index')

    if user.role == User.Role.TEACHER:
        return reverse('dashboard_teacher:index')

    if user.role == User.Role.LEARNER:
        return reverse('dashboard_learner:index')

    return reverse('main:home')


def create_learner_user(*, form):
    user = form.save(commit=False)
    user.role = User.Role.LEARNER
    user.is_active = False
    user.is_staff = False
    user.save()

    return user


def create_teacher_user(*, form, agreement_accepted_at=None):
    user = form.save(commit=False)
    user.role = User.Role.TEACHER
    user.is_active = False
    user.is_staff = False
    user.save()

    Teacher.objects.create(
        user=user,
        city=form.cleaned_data.get('city'),
        school=form.cleaned_data.get('school'),
        agreement_accepted_at=agreement_accepted_at,
    )

    return user


def activate_user(user):
    user.is_active = True
    user.save(update_fields=['is_active'])

    return user
