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
        ('manager', _('Manager')),
        ('admin', _('Admin')),
    )

    email = models.EmailField(_('email'), max_length=128, unique=True)
    username = models.CharField(_('username'), max_length=128, unique=True, validators=[UnicodeUsernameValidator()])
    first_name = models.CharField(_('First name'), max_length=128)
    last_name = models.CharField(_('Last name'), max_length=128)
    avatar = models.ImageField(_('Avatar'), upload_to='core/generics/accounts/users/', blank=True, null=True)
    google_avatar = models.URLField(_('Google avatar'), blank=True, null=True)
    user_role = models.CharField(_('User role'), max_length=32, choices=USER_ROLE, default='learner')
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
        return self.email or self.username

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def role(self):
        if self.user_role == 'learner':
            return getattr(self, 'learner', None)
        elif self.user_role == 'teacher':
            return getattr(self, 'teacher', None)
        elif self.user_role == 'manager':
            return getattr(self, 'manager', None)
        return None

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


# Roles
# ----------------------------------------------------------------------------------------------------------------------
# Learner
class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner', verbose_name=_('User'))
    school = models.ForeignKey(
        'School', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='learners', verbose_name=_('School')
    )
    school_class = models.ForeignKey(
        'schools.SchoolClass', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='learners', verbose_name=_('School class')
    )

    class Meta:
        verbose_name = _('Learner')
        verbose_name_plural = _('Learners')

    def __str__(self):
        return _('Learner: {}').format(self.user.get_full_name())


# Teacher
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher', verbose_name=_('User'))
    school = models.ForeignKey(
        'School', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='teachers', verbose_name=_('School')
    )
    subjects = models.ManyToManyField('Subject', blank=True, related_name='teachers', verbose_name=_('Subjects'))
    is_homeroom_teacher = models.BooleanField(_('Is homeroom teacher'), default=False)

    class Meta:
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')

    def __str__(self):
        return self.user.get_full_name()


# Manager
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager', verbose_name=_('User'))
    school = models.ForeignKey(
        'School', on_delete=models.CASCADE, null=True, blank=True,
        related_name='managers', verbose_name=_('School')
    )
    activity = models.CharField(_('Activity'), max_length=100, default='Director')

    class Meta:
        verbose_name = _('Manager')
        verbose_name_plural = _('Managers')

    def __str__(self):
        return _('Manager: {}').format(self.user.get_full_name())
