from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


# -------------- City --------------
class City(BaseModel):
    name = models.CharField(_('Name'), max_length=128, unique=True)

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ('name',)

    def __str__(self):
        return self.name


# -------------- School --------------
class School(BaseModel):
    city = models.ForeignKey(
        City, verbose_name=_('City'),
        on_delete=models.PROTECT, related_name='schools',
    )
    name = models.CharField(_('Name'), max_length=255)

    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')
        ordering = ('city__name', 'name')
        unique_together = ('city', 'name')

    def __str__(self):
        return self.name
