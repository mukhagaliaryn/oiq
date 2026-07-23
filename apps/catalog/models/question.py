from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from .content import Topic


# -------------- QuestionFormat --------------
class QuestionFormat(models.Model):
    name = models.CharField(_('Name'), max_length=64)
    code = models.SlugField(_('Code'), max_length=64, unique=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0, unique=True)

    class Meta:
        verbose_name = _('Question format')
        verbose_name_plural = _('Question formats')
        ordering = ('order', )

    def __str__(self):
        return self.name


# -------------- FormatVariant --------------
class FormatVariant(models.Model):
    format = models.ForeignKey(
        QuestionFormat, on_delete=models.CASCADE,
        related_name='variants', verbose_name=_('Format')
    )
    name = models.CharField(_('Name'), max_length=64)
    code = models.SlugField(_('Code'), max_length=64)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Question variant')
        verbose_name_plural = _('Question variants')
        ordering = ('order', )

    def __str__(self):
        return self.name


# -------------- Question --------------
class Question(BaseModel):
    class Level(models.TextChoices):
        EASY = 'easy', _('Easy')
        MEDIUM = 'medium', _('Medium')
        HARD = 'hard', _('Hard')

    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Topic')
    )
    author = models.ForeignKey(
        'accounts.Teacher', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='questions', verbose_name=_('Author')
    )
    text = models.TextField(_('Text'))
    format = models.ForeignKey(
        QuestionFormat, on_delete=models.PROTECT,
        related_name='questions', verbose_name=_('Format')
    )
    variant = models.ForeignKey(
        FormatVariant, on_delete=models.PROTECT, null=True, blank=True,
        related_name='questions', verbose_name=_('Variant')
    )
    level = models.CharField(_('Level'), choices=Level.choices, max_length=16, default=Level.EASY)
    time_limit = models.PositiveSmallIntegerField(_('Time limit (sec)'), default=30)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return _('#{} question').format(self.pk)


# -------------- Option --------------
class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='options', verbose_name=_('Question')
    )
    answer = models.TextField(_('Answer'))
    is_correct = models.BooleanField(_('Is correct'), default=False)

    class Meta:
        verbose_name = _('Option')
        verbose_name_plural = _('Options')

    def __str__(self):
        return _('#{} option').format(self.pk)


# -------------- MatchPair --------------
class MatchPair(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='match_pairs', verbose_name=_('Question')
    )
    left = models.TextField(_('Left item'))
    right = models.TextField(_('Right item'))
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Match pair')
        verbose_name_plural = _('Match pairs')
        ordering = ('order',)

    def __str__(self):
        return _('#{} match pair').format(self.pk)
