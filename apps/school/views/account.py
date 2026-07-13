from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.accounts.services import change_password, update_basic_info
from apps.school.forms.account import BasicInfoForm, ChangePasswordForm


# -------------- account_view --------------
def account_view(request, org):
    user = request.user

    basic_form = BasicInfoForm(initial={
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
    })
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            basic_form = BasicInfoForm(request.POST)

            if basic_form.is_valid():
                update_basic_info(
                    user,
                    first_name=basic_form.cleaned_data['first_name'],
                    last_name=basic_form.cleaned_data['last_name'],
                    phone=basic_form.cleaned_data['phone'],
                )
                messages.success(request, _('Profile has been updated.'))
                return redirect('school:account', org=org)

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
                    return redirect('school:account', org=org)

    context = {
        'organization': request.organization,
        'membership': request.membership,
        'basic_form': basic_form,
        'password_form': password_form,
    }
    return render(request, 'school/account.html', context)
