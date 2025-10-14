from django.contrib.auth.forms import UserCreationForm
from core.generics.models import User


# UserRegisterForm
# ----------------------------------------------------------------------------------------------------------------------
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', )
