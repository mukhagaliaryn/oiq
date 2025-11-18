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
# Question model
class Question(models.Model):
    LEVEL = (
        ('easy', _('Easy')),
        ('medium', _('Medium')),
        ('hard', _('Hard')),
    )

    body = models.TextField(_('Body'))
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Topic')
    )
    level = models.CharField(_('Level'), choices=LEVEL, max_length=16, default='easy')

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return f'{self.pk}-question'


# QuestionType model
class QuestionType(models.Model):
    QUESTION_TYPE = (
        ('none', _('None')),
        ('test', _('Test')),
        ('matching', _('Matching')),
        ('written', _('Written')),
    )

    FEATURES = (
        ('none', _('None')),
        (
            _('Test features'), (
                ('single', _('Single')),
                ('multiple', _('Multiple')),
            ),
        ),
        (
            _('Matching features'), (
                ('col', _('Column')),
                ('row', _('Row')),
            ),
        ),
    )

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='question_types', verbose_name=_('Question')
    )
    question_type = models.CharField(_('Question type'), max_length=16, choices=QUESTION_TYPE, default='none')
    feature = models.CharField(_('Feature'), max_length=16, choices=FEATURES, default='none')

    class Meta:
        verbose_name = _('Question type')
        verbose_name_plural = _('Question types')

    def __str__(self):
        return f'{self.get_question_type_display()} {self.get_feature_display()}'


# Question variants
# ----------------------------------------------------------------------------------------------------------------------
# Option
class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='options', verbose_name=_('Question')
    )
    answer = models.TextField(_('Answer'))
    is_correct = models.BooleanField(_('Is correct'), default=False)

    def __str__(self):
        return _('{}-answer').format(self.pk)
