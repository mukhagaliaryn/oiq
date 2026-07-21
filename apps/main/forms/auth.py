from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from apps.catalog.selectors import get_active_subjects, get_cities, get_schools_by_city

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Email or username'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput())


class BaseRegisterForm(UserCreationForm):
    first_name = forms.CharField(label=_('First name'), max_length=100)
    last_name = forms.CharField(label=_('Last name'), max_length=100)
    email = forms.EmailField(label=_('Email'))
    agreement = forms.BooleanField(
        label=_('I agree with terms'),
        required=True,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'agreement')

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('User with this email already exists.'))

        return email


class LearnerRegisterForm(BaseRegisterForm):
    pass


class TeacherRegisterForm(BaseRegisterForm):
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
