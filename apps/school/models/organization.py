from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


# -------------- Organization --------------
class Organization(BaseModel):
    school = models.ForeignKey(
        'directory.School', verbose_name=_('School'),
        on_delete=models.SET_NULL, related_name='organizations',
        blank=True, null=True,
    )
    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), unique=True)

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ('name',)

    def __str__(self):
        return self.name


# -------------- OrgRole --------------
class OrgRole(models.TextChoices):
    SYS_ADMIN = 'sys_admin', _('System administrator')
    DIRECTOR = 'director', _('Director')
    DEPUTY_ACADEMIC = 'deputy_academic', _('Deputy director (academic)')
    DEPUTY_UPBRINGING = 'deputy_upbringing', _('Deputy director (upbringing)')
    HOMEROOM = 'homeroom', _('Homeroom teacher')
    TEACHER = 'teacher', _('Subject teacher')
    STUDENT = 'student', _('Student')
    PARENT = 'parent', _('Parent')


# -------------- Membership --------------
class Membership(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('User'),
        on_delete=models.CASCADE, related_name='memberships',
    )
    organization = models.ForeignKey(
        Organization, verbose_name=_('Organization'),
        on_delete=models.CASCADE, related_name='memberships',
    )
    roles = ArrayField(
        models.CharField(max_length=32, choices=OrgRole.choices),
        verbose_name=_('Roles'), default=list,
    )

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')
        ordering = ('organization', 'user')
        constraints = [
            models.UniqueConstraint(fields=['user', 'organization'], name='uniq_member'),
        ]

    def __str__(self):
        return f'{self.user} — {self.organization}'

    def has_role(self, *roles):
        return any(role in self.roles for role in roles)
