from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


# User model
# ----------------------------------------------------------------------------------------------------------------------
# User manager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        if not username:
            raise ValueError(_('The user must have an username'))
        if not email:
            raise ValueError(_('The user must have an email address'))

        email = self.normalize_email(email)
        user = self.model(username=username.lower(), email=email.lower(), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **kwargs):
        user = self.create_user(username, email, password=password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# User model
class User(AbstractBaseUser, PermissionsMixin):
    USER_ROLE = (
        ('learner', _('Learner')),
        ('teacher', _('Teacher')),
        ('admin', _('Admin')),
    )

    email = models.EmailField(_('email'), max_length=64, unique=True)
    username = models.CharField(_('username'), max_length=64, unique=True, validators=[UnicodeUsernameValidator()])
    first_name = models.CharField(_('First name'), max_length=64)
    last_name = models.CharField(_('Last name'), max_length=64)
    avatar = models.ImageField(_('Avatar'), upload_to='users/avatars/%Y/%m/%d/', blank=True, null=True)
    user_role = models.CharField(_('User role'), max_length=16, choices=USER_ROLE, default='learner')
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_(
            'Designates whether this user should be treated as active.'
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
