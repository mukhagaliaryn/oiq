from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from apps.accounts.decorators import learner_required
from apps.accounts.services import change_password, deactivate_account, remove_avatar, set_avatar, update_basic_info
from apps.learning.forms.account import AccountDeleteForm, BasicInfoForm, ChangePasswordForm

LANGUAGE_NATIVE_NAMES = {
    'kk': 'Қазақ',
    'ru': 'Русский',
    'en': 'English',
}


# -------------- account_view --------------
@learner_required
def account_view(request):
    user = request.user

    basic_form = BasicInfoForm(initial={
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
    })
    password_form = ChangePasswordForm()
    delete_form = AccountDeleteForm(user=user)

    class _SettingsForm(forms.Form):
        language = forms.ChoiceField(
            choices=[(code, LANGUAGE_NATIVE_NAMES.get(code, name)) for code, name in settings.LANGUAGES],
        )

    settings_form = _SettingsForm(initial={'language': get_language()})

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'remove_avatar':
            remove_avatar(user)
            messages.success(request, _('Avatar removed.'))
            return redirect('learning:account')

        elif action == 'update_profile':
            basic_form = BasicInfoForm(request.POST, request.FILES)

            if basic_form.is_valid():
                update_basic_info(
                    user,
                    first_name=basic_form.cleaned_data['first_name'],
                    last_name=basic_form.cleaned_data['last_name'],
                    phone=basic_form.cleaned_data['phone'],
                )

                if basic_form.cleaned_data.get('avatar'):
                    set_avatar(user, basic_form.cleaned_data['avatar'])

                messages.success(request, _('Profile has been updated.'))
                return redirect('learning:account')

        elif action == 'change_password':
            password_form = ChangePasswordForm(request.POST)

            if password_form.is_valid():
                try:
                    change_password(
                        user,
                        password_form.cleaned_data['old_password'],
                        password_form.cleaned_data['new_password1'],
                    )
                except ValidationError as exc:
                    password_form.add_error(None, exc)
                else:
                    update_session_auth_hash(request, user)
                    messages.success(request, _('Password has been changed.'))
                    return redirect('learning:account')

        elif action == 'delete_account':
            delete_form = AccountDeleteForm(request.POST, user=user)

            if delete_form.is_valid():
                deactivate_account(user)
                logout(request)
                messages.success(request, _('Your account has been deactivated.'))
                return redirect('main:login')

    context = {
        'basic_form': basic_form,
        'password_form': password_form,
        'delete_form': delete_form,
        'settings_form': settings_form,
    }
    return render(request, 'learning/account.html', context)
