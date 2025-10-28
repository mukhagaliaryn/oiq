from django.db import models
from django.utils.translation import gettext_lazy as _


# School global
# ----------------------------------------------------------------------------------------------------------------------
# School model
class School(models.Model):
    SCHOOL_TYPE = (
        ('state', _('State')),
        ('private', _('Private')),
        ('cozy', _('Cozy')),
    )
    name = models.CharField(_('Name'), max_length=255)
    school_type = models.CharField(_('Type'), max_length=16, default='state', choices=SCHOOL_TYPE)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')
        ordering = ('order', )


# Class global
# ----------------------------------------------------------------------------------------------------------------------
# Class model
class Class(models.Model):
    grade = models.PositiveSmallIntegerField(_('Grade'))

    def __str__(self):
        return _('{}-class').format(self.grade)

    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')
        ordering = ('grade', )


# Letter model
class Letter(models.Model):
    name = models.CharField(_('Name'), max_length=2)
    class_grade = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='letters', verbose_name=_('Class'))
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    def __str__(self):
        return _('{}{} - class').format(self.class_grade.grade, self.name)

    class Meta:
        verbose_name = _('Letter')
        verbose_name_plural = _('Letters')
        ordering = ('order', )
