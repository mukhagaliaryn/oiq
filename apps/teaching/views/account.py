from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from apps.accounts.decorators import teacher_required
from apps.accounts.selectors import get_teacher, get_teacher_by_username
from apps.accounts.services import (
    change_password, deactivate_account, remove_avatar, set_avatar,
    update_basic_info, update_teacher_profile,
)
from apps.teaching.forms.account import (
    AccountDeleteForm, BasicInfoForm, ChangePasswordForm, TeacherProfileForm,
)

LANGUAGE_NATIVE_NAMES = {
    'kk': 'Қазақ',
    'ru': 'Русский',
    'en': 'English',
}


# -------------- profile view --------------
@teacher_required
def profile_view(request, username):
    profile_user = get_teacher_by_username(username)

    if profile_user is None:
        raise Http404

    context = {
        'profile_user': profile_user,
        'is_own_profile': profile_user == request.user,
    }
    return render(request, 'teaching/account/profile/page.html', context)


# -------------- account edit view --------------
@teacher_required
def account_edit_view(request):
    user = request.user
    teacher = get_teacher(user)

    if request.method == 'POST' and 'remove_avatar' in request.POST:
        remove_avatar(user)
        messages.success(request, _('Avatar removed.'))
        return redirect('teaching:account-edit')

    basic_form = BasicInfoForm(request.POST or None, request.FILES or None, initial={
        'first_name': user.first_name,
        'last_name': user.last_name,
        'middle_name': user.middle_name,
        'phone': user.phone,
    })
    teacher_form = TeacherProfileForm(request.POST or None, initial={
        'city': teacher.city_id,
        'school': teacher.school_id,
        'subject': teacher.subject_id,
    })

    if request.method == 'POST':
        if basic_form.is_valid() and teacher_form.is_valid():
            update_basic_info(
                user,
                first_name=basic_form.cleaned_data['first_name'],
                last_name=basic_form.cleaned_data['last_name'],
                middle_name=basic_form.cleaned_data['middle_name'],
                phone=basic_form.cleaned_data['phone'],
            )

            if basic_form.cleaned_data.get('avatar'):
                set_avatar(user, basic_form.cleaned_data['avatar'])

            update_teacher_profile(
                teacher,
                city=teacher_form.cleaned_data['city'],
                school=teacher_form.cleaned_data['school'],
                subject=teacher_form.cleaned_data['subject'],
            )

            messages.success(request, _('Profile has been updated.'))
            return redirect('teaching:account-edit')

    context = {
        'user_form': basic_form,
        'teacher_form': teacher_form,
    }
    return render(request, 'teaching/account/edit/page.html', context)


# -------------- account settings view --------------
@teacher_required
def account_settings_view(request):
    class _SettingsForm(forms.Form):
        language = forms.ChoiceField(
            choices=[(code, LANGUAGE_NATIVE_NAMES.get(code, name)) for code, name in settings.LANGUAGES],
        )

    form = _SettingsForm(initial={'language': get_language()})
    return render(request, 'teaching/account/settings/page.html', {'form': form})


# -------------- account security view --------------
@teacher_required
def account_security_view(request):
    password_form = ChangePasswordForm()
    delete_form = AccountDeleteForm(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_password':
            password_form = ChangePasswordForm(request.POST)

            if password_form.is_valid():
                try:
                    change_password(
                        request.user,
                        password_form.cleaned_data['old_password'],
                        password_form.cleaned_data['new_password1'],
                    )
                except ValidationError as exc:
                    password_form.add_error(None, exc)
                else:
                    update_session_auth_hash(request, request.user)
                    messages.success(request, _('Password has been changed.'))
                    return redirect('teaching:account-security')

        elif action == 'delete_account':
            delete_form = AccountDeleteForm(request.POST, user=request.user)

            if delete_form.is_valid():
                deactivate_account(request.user)
                logout(request)
                messages.success(request, _('Your account has been deactivated.'))
                return redirect('main:login')

    context = {
        'password_form': password_form,
        'delete_form': delete_form,
    }
    return render(request, 'teaching/account/security/page.html', context)
