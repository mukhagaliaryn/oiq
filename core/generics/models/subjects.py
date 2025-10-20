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


# Chapter model
class Chapter(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        related_name='chapters', verbose_name=_('Subject')
    )
    user_class = models.ForeignKey(
        'generics.Class', on_delete=models.CASCADE,
        related_name='chapters', verbose_name=_('Class'),
        blank=True, null=True
    )
    title = models.CharField(_('Title'), max_length=255)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Chapter')
        verbose_name_plural = _('Chapters')
        ordering = ('subject', 'user_class', 'order')
        unique_together = ('subject', 'user_class', 'title')

    def __str__(self):
        if self.user_class:
            return self.title
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
# QuestionType model
class QuestionType(models.Model):
    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=128, unique=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Question type')
        verbose_name_plural = _('Question types')

    def __str__(self):
        return self.name


# Question model
class Question(models.Model):
    LEVEL = (
        ('easy', _('Easy')),
        ('medium', _('Medium')),
        ('hard', _('Hard')),
    )

    title = models.CharField(_('Title'), max_length=128)
    body = models.TextField(_('Body'))
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Topic')
    )
    question_type = models.ForeignKey(
        QuestionType, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Question type')
    )
    level = models.CharField(_('Level'), choices=LEVEL, max_length=16, default='easy')
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return self.title
