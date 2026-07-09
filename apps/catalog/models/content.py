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
        'directory.Grade', verbose_name=_('Grades'),
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
    grade = models.ForeignKey(
        'directory.Grade', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='chapters', verbose_name=_('Grade')
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
        constraints = [
            models.UniqueConstraint(
                fields=['chapter', 'title'],
                condition=models.Q(is_active=True),
                name='unique_active_topic_title_per_chapter',
            )
        ]

    def __str__(self):
        return self.title
