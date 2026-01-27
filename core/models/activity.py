from django.db import models
from django.utils.translation import gettext_lazy as _


# Activity
# ----------------------------------------------------------------------------------------------------------------------
# Activity model
class Activity(models.Model):
    class ActivityType(models.TextChoices):
        GAME = 'game', _('Game')
        LIMITLESS = 'simulator', _('Simulator')

    class PlayMode(models.TextChoices):
        SPEED = 'speed', _('Speed')
        CLASSIC = 'classic', _('Classic')

    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=128, unique=True)
    activity_type = models.CharField(
        _('Activity type'),
        max_length=16,
        choices=ActivityType.choices,
        default=ActivityType.GAME
    )
    play_mode = models.CharField(
        _('Play mode'),
        max_length=16,
        choices=PlayMode.choices,
        default=PlayMode.SPEED
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

    def save(self, *args, **kwargs):
        if self.activity_type == 'simulator':
            self.play_mode = 'classic'
        super().save(*args, **kwargs)
