from django.db import models
from django.utils.translation import gettext_lazy as _


# Activity
# ----------------------------------------------------------------------------------------------------------------------
# Activity model
class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('game', _('Game')),
        ('simulator', _('Simulator')),
    )

    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=128, unique=True)
    activity_type = models.CharField(
        _('Activity type'), max_length=64,
        choices=ACTIVITY_TYPES, default='game'
    )
    question_formats = models.ManyToManyField(
        'core.QuestionFormat', related_name='activities', verbose_name=_('Question formats')
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
        ordering = ('order', )

    def __str__(self):
        return self.name
