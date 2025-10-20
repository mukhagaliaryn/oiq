from django.db import models
from django.utils.translation import gettext_lazy as _
from core.generics.models import User


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
    address = models.CharField(_('Address'), max_length=255, blank=True, null=True)
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


# ClassType model
class Letter(models.Model):
    name = models.CharField(_('Name'), max_length=2, unique=True)
    class_grade = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='letters', verbose_name=_('Class'))
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    def __str__(self):
        return _('{}{} - class').format(self.class_grade, self.name)

    class Meta:
        unique_together = ('class_grade', 'name')
        verbose_name = _('Letter')
        verbose_name_plural = _('Letters')
        ordering = ('order', )


# Defined school
# ----------------------------------------------------------------------------------------------------------------------
# SchoolClass
class SchoolClass(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name='school_classes', verbose_name=_('School')
    )
    user_class = models.ForeignKey(
        Class, on_delete=models.CASCADE,
        related_name='school_links', verbose_name=_('Class')
    )
    homeroom_teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, limit_choices_to={'user_type': 'teacher'},
        null=True, blank=True, verbose_name=_('Homeroom teacher')
    )

    class Meta:
        unique_together = ('school', 'user_class')
        verbose_name = _('School class')
        verbose_name_plural = _('School classes')

    def __str__(self):
        return f"{self.school.name} – {self.user_class}"


# SchoolSubject model
class SchoolSubject(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name='school_subjects', verbose_name=_('School')
    )
    subject = models.ForeignKey(
        'generics.Subject', on_delete=models.CASCADE,
        related_name='school_subjects', verbose_name=_('Subject')
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        unique_together = ('school', 'subject')
        verbose_name = _('School subject')
        verbose_name_plural = _('School subjects')
        ordering = ('order', )

    def __str__(self):
        return f"{self.subject.name} - {self.school.name}"


# ClassSubject model
class ClassSubject(models.Model):
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE,
        related_name='class_subjects', verbose_name=_('School class')
    )
    school_subject = models.ForeignKey(
        SchoolSubject, on_delete=models.CASCADE,
        related_name='class_subjects', verbose_name=_('School subject')
    )
    teachers = models.ManyToManyField(
        User, limit_choices_to={'user_type': 'teacher'},
        related_name='school_subjects', blank=True, verbose_name=_('Teachers')
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        unique_together = ('school_class', 'school_subject')
        verbose_name = _('Class subject')
        verbose_name_plural = _('Class subjects')
        ordering = ('order', )

    @property
    def subject(self):
        return self.school_subject.subject

    def __str__(self):
        return f"{self.school_class.user_class}–сынып. {self.subject}"
