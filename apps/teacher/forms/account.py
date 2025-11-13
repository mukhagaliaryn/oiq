from django import forms
from core.generics.models import User



class TeacherAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'email', 'username', )
