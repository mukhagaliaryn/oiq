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
            return f"{self.user_class}: {self.title}"
        return self.title


# Topic model
class Topic(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,
        related_name='topics', verbose_name=_('Chapter')
    )
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        ordering = ('chapter', 'order', 'id')
        unique_together = ('chapter', 'title')

    def __str__(self):
        return self.title

