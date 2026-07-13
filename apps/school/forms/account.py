from django import forms
from django.utils.translation import gettext_lazy as _

_INPUT_CLASS = 'w-full rounded-full border border-default bg-neutral-primary px-6 py-3 outline-none transition focus:ring-2 focus:ring-brand'


# -------------- BasicInfoForm --------------
class BasicInfoForm(forms.Form):
    first_name = forms.CharField(
        label=_('First name'), max_length=150,
        widget=forms.TextInput(attrs={'class': _INPUT_CLASS}),
    )
    last_name = forms.CharField(
        label=_('Last name'), max_length=150,
        widget=forms.TextInput(attrs={'class': _INPUT_CLASS}),
    )
    phone = forms.CharField(
        label=_('Phone'), max_length=32, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT_CLASS}),
    )


# -------------- ChangePasswordForm --------------
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label=_('Current password'),
        widget=forms.PasswordInput(attrs={'class': _INPUT_CLASS}),
    )
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(attrs={'class': _INPUT_CLASS}),
    )
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        widget=forms.PasswordInput(attrs={'class': _INPUT_CLASS}),
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('new_password1') and cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise forms.ValidationError(_('Passwords do not match.'))

        return cleaned_data
