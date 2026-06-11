from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


# Subject models
# ----------------------------------------------------------------------------------------------------------------------
# -------------- Subject --------------
class Subject(BaseModel):
    name = models.CharField(_('Name'), max_length=128)
    cover = models.ImageField(_('Cover'), upload_to='subjects/covers/', blank=True, null=True)
    grades = models.ManyToManyField(
        'core.Grade', verbose_name=_('Grades'),
        related_name='subjects', blank=True,
    )
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ('order', )


# -------------- Chapter --------------
class Chapter(BaseModel):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        related_name='chapters', verbose_name=_('Subject')
    )
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Chapter')
        verbose_name_plural = _('Chapters')
        ordering = ('order', )

    def __str__(self):
        return self.title


# -------------- Topic --------------
class Topic(BaseModel):
    title = models.CharField(_('Title'), max_length=255)
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,
        related_name='topics', verbose_name=_('Chapter')
    )
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        ordering = ('order', )
        unique_together = ('chapter', 'title')

    def __str__(self):
        return self.title


# Question models
# ----------------------------------------------------------------------------------------------------------------------
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


# -------------- QuestionVariant --------------
class QuestionVariant(models.Model):
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
    text = models.TextField(_('Text'))
    format = models.ForeignKey(
        QuestionFormat, on_delete=models.PROTECT,
        related_name='questions', verbose_name=_('Format')
    )
    variant = models.ForeignKey(
        QuestionVariant, on_delete=models.PROTECT, null=True, blank=True,
        related_name='questions', verbose_name=_('Variant')
    )
    level = models.CharField(_('Level'), choices=Level.choices, max_length=16, default=Level.EASY)
    time_limit = models.PositiveSmallIntegerField(_('Time limit (sec)'), default=30)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return _('#{} question').format(self.pk)


# Question variants
# ----------------------------------------------------------------------------------------------------------------------
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
