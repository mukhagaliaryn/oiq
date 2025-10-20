from django.db import models
from django.utils.translation import gettext_lazy as _


# Game model
# ----------------------------------------------------------------------------------------------------------------------
class Game(models.Model):
    name = models.CharField(_('Name'), max_length=128)
    order = models.SmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Game')
        verbose_name_plural = _('Games')
        ordering = ('order', )

    def __str__(self):
        return self.name



# Virtual model
# ----------------------------------------------------------------------------------------------------------------------
class Virtual(models.Model):
    name = models.CharField(_('Name'), max_length=128)
    order = models.SmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Virtual')
        verbose_name_plural = _('Virtuals')
        ordering = ('order', )

    def __str__(self):
        return self.name
