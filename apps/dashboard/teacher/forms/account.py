from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core.models import City, School, Teacher

User = get_user_model()


class UserEditForm(forms.ModelForm):
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

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name', 'phone', 'avatar')


class TeacherEditForm(forms.ModelForm):
    city = forms.ModelChoiceField(
        label=_('City'),
        queryset=City.objects.filter(is_active=True).order_by('name'),
        required=True,
        empty_label=_('Select city'),
    )
    school = forms.ModelChoiceField(
        label=_('School'),
        queryset=School.objects.none(),
        required=True,
        empty_label=_('Select school'),
    )

    class Meta:
        model = Teacher
        fields = ('city', 'school')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        city_id = self.data.get('city') or self.initial.get('city') or self.instance.city_id

        if city_id:
            self.fields['school'].queryset = (
                School.objects
                .filter(city_id=city_id, is_active=True)
                .order_by('name')
            )


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
