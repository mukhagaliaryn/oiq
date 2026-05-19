from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel, BaseModel
from core.utils.files import user_avatar_upload_path


# Role model
# ----------------------------------------------------------------------------------------------------------------------
class Role(TimeStampedModel):
    code = models.SlugField(_('Code'), max_length=64, unique=True)
    name = models.CharField(_('Name'), max_length=128)

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ('name',)

    def __str__(self):
        return self.name


# User model
# ----------------------------------------------------------------------------------------------------------------------
# -------------- User --------------
class User(AbstractUser):
    middle_name = models.CharField(_('Middle name'), max_length=128, blank=True)
    phone = models.CharField(_('Phone'), max_length=32, blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to=user_avatar_upload_path, blank=True, null=True)
    is_verified = models.BooleanField(_('Is verified'), default=False)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('id',)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return ' '.join(filter(None, [self.first_name, self.last_name])) or self.username

    @property
    def full_name(self):
        return ' '.join(filter(None, [self.first_name, self.middle_name, self.last_name])) or self.username

    @property
    def role(self):
        return self.user_role.role if hasattr(self, 'user_role') else None


# -------------- UserRole --------------
class UserRole(BaseModel):
    user = models.OneToOneField(
        User, verbose_name=_('User'),
        on_delete=models.CASCADE, related_name='user_role',
    )
    role = models.ForeignKey(
        Role, verbose_name=_('Role'),
        on_delete=models.PROTECT, related_name='user_roles',
    )
    is_system = models.BooleanField(_('Is system'), default=False)

    class Meta:
        verbose_name = _('User role')
        verbose_name_plural = _('User roles')
        ordering = ('user', 'role')

    def __str__(self):
        return f'{self.user} — {self.role}'


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
