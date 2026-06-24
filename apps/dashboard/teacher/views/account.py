from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from apps.dashboard.teacher.forms.account import AccountDeleteForm, TeacherEditForm, UserEditForm
from core.utils.decorators import teacher_required

User = get_user_model()

LANGUAGE_NATIVE_NAMES = {
    'kk': 'Қазақ',
    'ru': 'Русский',
    'en': 'English',
}


# -------------- profile view --------------
@teacher_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username, role=User.Role.TEACHER)

    context = {
        'profile_user': profile_user,
        'is_own_profile': profile_user == request.user,
    }
    return render(request, 'app/dashboard/teacher/account/profile.html', context)


# -------------- account edit view --------------
@teacher_required
def account_edit_view(request):
    user = request.user

    if request.method == 'POST' and 'remove_avatar' in request.POST:
        if user.avatar:
            user.avatar.delete(save=False)
            user.save(update_fields=['avatar'])
            messages.success(request, _('Avatar removed.'))

        return redirect('teacher:account-edit')

    user_form = UserEditForm(request.POST or None, request.FILES or None, instance=user)
    teacher_form = TeacherEditForm(request.POST or None, instance=user.teacher)

    if request.method == 'POST':
        if user_form.is_valid() and teacher_form.is_valid():
            user_form.save()
            teacher_form.save()
            messages.success(request, _('Profile has been updated.'))
            return redirect('teacher:account-edit')

    context = {
        'user_form': user_form,
        'teacher_form': teacher_form,
    }
    return render(request, 'app/dashboard/teacher/account/edit.html', context)


# -------------- account settings view --------------
@teacher_required
def account_settings_view(request):
    class _SettingsForm(forms.Form):
        language = forms.ChoiceField(
            choices=[(code, LANGUAGE_NATIVE_NAMES.get(code, name)) for code, name in settings.LANGUAGES],
        )

    form = _SettingsForm(initial={'language': get_language()})
    return render(request, 'app/dashboard/teacher/account/settings.html', {'form': form})


# -------------- account security view --------------
@teacher_required
def account_security_view(request):
    password_form = PasswordChangeForm(user=request.user)
    delete_form = AccountDeleteForm(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Password has been changed.'))
                return redirect('teacher:account-security')

        elif action == 'delete_account':
            delete_form = AccountDeleteForm(request.POST, user=request.user)

            if delete_form.is_valid():
                user = request.user
                user.is_active = False
                user.save(update_fields=['is_active'])
                logout(request)
                messages.success(request, _('Your account has been deactivated.'))
                return redirect('main:login')

    context = {
        'password_form': password_form,
        'delete_form': delete_form,
    }
    return render(request, 'app/dashboard/teacher/account/security.html', context)
