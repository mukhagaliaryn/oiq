from django import forms
from django.utils.translation import gettext_lazy as _
from apps.catalog.selectors import get_active_subjects
from apps.directory.selectors import get_cities, get_schools_by_city


# -------------- BasicInfoForm --------------
class BasicInfoForm(forms.Form):
    first_name = forms.CharField(label=_('First name'), max_length=150)
    last_name = forms.CharField(label=_('Last name'), max_length=150)
    middle_name = forms.CharField(label=_('Middle name'), max_length=128, required=False)
    phone = forms.CharField(label=_('Phone'), max_length=32, required=False)
    avatar = forms.ImageField(
        label=_('Avatar'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'x-ref': 'avatarInput',
            '@change': 'onAvatarChange($event)',
        }),
    )


# -------------- TeacherProfileForm --------------
class TeacherProfileForm(forms.Form):
    city = forms.ModelChoiceField(
        label=_('City'),
        queryset=get_cities().order_by('name'),
        required=True,
        empty_label=_('Select city'),
    )
    school = forms.ModelChoiceField(
        label=_('School'),
        queryset=get_schools_by_city(None),
        required=True,
        empty_label=_('Select school'),
    )
    subject = forms.ModelChoiceField(
        label=_('Subject'),
        queryset=get_active_subjects(),
        required=True,
        empty_label=_('Select subject'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        city_id = self.data.get('city') or self.initial.get('city')

        if city_id:
            self.fields['school'].queryset = get_schools_by_city(city_id)


# -------------- ChangePasswordForm --------------
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label=_('Current password'), widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_('New password'), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_('Confirm new password'), widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('new_password1') and cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise forms.ValidationError(_('Passwords do not match.'))

        return cleaned_data


# -------------- AccountDeleteForm --------------
class AccountDeleteForm(forms.Form):
    password = forms.CharField(
        label=_('Confirm with your password'),
        widget=forms.PasswordInput(),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']

        if not self.user.check_password(password):
            raise forms.ValidationError(_('Incorrect password.'))

        return password
