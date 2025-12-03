from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags


# Subject
# ----------------------------------------------------------------------------------------------------------------------
# Subject model
class Subject(models.Model):
    name = models.CharField(_('Name'), max_length=128)
    order = models.PositiveSmallIntegerField(_('Order'), default=0, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ('order', )


# Chapter model
class Chapter(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        related_name='chapters', verbose_name=_('Subject')
    )
    title = models.CharField(_('Title'), max_length=255)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Chapter')
        verbose_name_plural = _('Chapters')
        ordering = ('order', )

    def __str__(self):
        return self.title


# Topic model
class Topic(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,
        related_name='topics', verbose_name=_('Chapter')
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        ordering = ('order', )
        unique_together = ('chapter', 'title')

    def __str__(self):
        return self.title


# Question
# ----------------------------------------------------------------------------------------------------------------------
# QuestionFormat model
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


# QuestionVariant model
class QuestionVariant(models.Model):
    format = models.ForeignKey(
        QuestionFormat, on_delete=models.CASCADE,
        related_name='variants', verbose_name=_('Format')
    )
    name = models.CharField(_('Name'), max_length=64)
    code = models.SlugField(_('Code'), max_length=64, unique=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Question variant')
        verbose_name_plural = _('Question variants')
        ordering = ('order', )

    def __str__(self):
        return self.name


# Question model
class Question(models.Model):
    LEVEL = (
        ('easy', _('Easy')),
        ('medium', _('Medium')),
        ('hard', _('Hard')),
    )

    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Topic')
    )
    body = models.TextField(_('Body'))
    format = models.ForeignKey(
        QuestionFormat, on_delete=models.PROTECT,
        related_name='questions', verbose_name=_('Format')
    )
    variant = models.ForeignKey(
        QuestionVariant, on_delete=models.PROTECT, null=True, blank=True,
        related_name='questions', verbose_name=_('Variant')
    )
    level = models.CharField(_('Level'), choices=LEVEL, max_length=16, default='easy')
    date_in = models.DateField(_('Date in'), auto_now_add=True)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return f'#{self.pk}-question'


# Question variants
# ----------------------------------------------------------------------------------------------------------------------
# Option model
class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='options', verbose_name=_('Question')
    )
    answer = models.TextField(_('Answer'))
    is_correct = models.BooleanField(_('Is correct'), default=False)

    def __str__(self):
        clean_text = strip_tags(self.answer)
        if len(clean_text) > 40:
            return f'#{self.pk}. {clean_text[:40]}...'
        return f'#{self.pk}. {clean_text}'
