from django.db import models
from django.utils.translation import gettext_lazy as _


class Interactive(models.Model):
    INTERACTIVE_TYPES = (
        ('game', _('Game')),
        ('simulator', _('Simulator')),
    )

    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    interactive_type = models.CharField(
        _('Interactive type'), max_length=100,
        default='game', choices=INTERACTIVE_TYPES
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Interactive')
        verbose_name_plural = _('Interactive')
        ordering = ('order', )

    def __str__(self):
        return self.name
