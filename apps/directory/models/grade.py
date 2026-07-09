from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


# -------------- Grade --------------
class Grade(BaseModel):
    name = models.CharField(_('Name'), max_length=64)
    code = models.SlugField(_('Code'), max_length=64)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Grade')
        verbose_name_plural = _('Grades')
        ordering = ('order', 'name')

    def __str__(self):
        return self.name
