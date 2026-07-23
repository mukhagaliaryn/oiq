from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# -------------- Teacher --------------
class Teacher(models.Model):
    class Type(models.TextChoices):
        REGULAR = 'regular', _('Regular')
        PARTNER = 'partner', _('Partner')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name=_('User'),
        on_delete=models.CASCADE, related_name='teacher',
    )
    city = models.ForeignKey(
        'catalog.City', verbose_name=_('City'),
        on_delete=models.SET_NULL, related_name='teachers',
        blank=True, null=True,
    )
    school = models.ForeignKey(
        'catalog.School', verbose_name=_('School'),
        on_delete=models.SET_NULL, related_name='teachers',
        blank=True, null=True,
    )
    subjects = models.ManyToManyField(
        'catalog.Subject', verbose_name=_('Subjects'),
        related_name='teachers', blank=True,
    )
    type = models.CharField(
        _('Type'), max_length=16,
        choices=Type.choices, default=Type.REGULAR,
    )
    agreement_accepted_at = models.DateTimeField(_('Agreement accepted at'), blank=True, null=True)

    class Meta:
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')
        ordering = ('user',)

    def __str__(self):
        return str(self.user)

    @property
    def is_partner(self):
        return self.type == self.Type.PARTNER
