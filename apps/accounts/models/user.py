from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.utils.files import user_avatar_upload_path


# -------------- User --------------
class User(AbstractUser):
    class AccountType(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        TEACHER = 'teacher', _('Teacher')
        LEARNER = 'learner', _('Learner')
        SCHOOL_USER = 'school_user', _('School system user')

    middle_name = models.CharField(_('Middle name'), max_length=128, null=True, blank=True)
    account_type = models.CharField(
        _('Account type'), max_length=16, choices=AccountType.choices,
        default=AccountType.LEARNER, help_text=_('Shows which product the user belongs to (teaching/learning/school).')
    )
    phone = models.CharField(_('Phone'), max_length=32, blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to=user_avatar_upload_path, blank=True, null=True)
    is_verified = models.BooleanField(
        _('Is verified'), default=False,
        help_text=_('Marks whether the user has confirmed their account (e.g. via email).'),
    )
    email = models.EmailField(_('Email address'), blank=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('id',)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return ' '.join(filter(None, [self.first_name, self.last_name])) or self.username

    display_name.fget.short_description = _('Full name')

    @property
    def full_name(self):
        return ' '.join(filter(None, [self.first_name, self.middle_name, self.last_name])) or self.username


# -------------- UserSession --------------
class UserSession(models.Model):
    class DeviceTypeChoices(models.TextChoices):
        DESKTOP = 'desktop', _('Desktop')
        MOBILE = 'mobile', _('Mobile')
        TABLET = 'tablet', _('Tablet')
        UNKNOWN = 'unknown', _('Unknown')

    user = models.ForeignKey(
        User, verbose_name=_('User'),
        on_delete=models.CASCADE, related_name='sessions',
    )
    session_key = models.CharField(_('Session key'), max_length=128, db_index=True)

    device_type = models.CharField(
        _('Device type'), max_length=16,
        choices=DeviceTypeChoices.choices, default=DeviceTypeChoices.UNKNOWN,
    )
    device_name = models.CharField(_('Device name'), max_length=128, blank=True)
    browser = models.CharField(_('Browser'), max_length=128, blank=True)
    os = models.CharField(_('Operating system'), max_length=128, blank=True)

    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('User agent'), blank=True)
    last_activity_at = models.DateTimeField(_('Last activity at'), blank=True, null=True)

    class Meta:
        verbose_name = _('User session')
        verbose_name_plural = _('User sessions')
        ordering = ('-last_activity_at',)

    def __str__(self):
        return f'{self.user} — {self.device_name or self.device_type}'
