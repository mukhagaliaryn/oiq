from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# -------------- LoginForm --------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Email or username'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput())

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if user.account_type != user.AccountType.SCHOOL_USER:
            raise ValidationError(
                _('This login page is only for school system users. '
                  'If you are a teacher or a learner, sign in at oiq.kz.'),
                code='not_school_user',
            )
