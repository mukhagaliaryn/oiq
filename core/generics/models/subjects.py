from django.db import models
from django.utils.translation import gettext_lazy as _


# Subject
# ----------------------------------------------------------------------------------------------------------------------
# Subject model
class Subject(models.Model):
    name = models.CharField(_('Name'), max_length=128)

    order = models.PositiveSmallIntegerField(_('Order'), default=0)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ('order', )
