from django.db import models
from django.utils.translation import gettext_lazy as _
from core.generics.models import User


# School
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


# Class
# ----------------------------------------------------------------------------------------------------------------------
# ClassType model
class ClassType(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name='class_types', verbose_name=_('School')
    )
    letter = models.CharField(_('Letter'), max_length=2, unique=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    def __str__(self):
        return self.letter

    class Meta:
        unique_together = ('school', 'letter')
        verbose_name = _('Class type')
        verbose_name_plural = _('Class types')
        ordering = ('order', )


# Class model
class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes', verbose_name=_('School'))
    grade = models.PositiveSmallIntegerField(_('Grade'))
    class_type = models.ForeignKey(
        ClassType, on_delete=models.CASCADE,
        related_name='classes', verbose_name=_('Class type')
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    def __str__(self):
        return f"{self.grade}{self.class_type.letter}"

    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')
        ordering = ('order', )


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
        return f"{self.school.name} – {self.subject.name}"


# ClassSubject model
class ClassSubject(models.Model):
    user_class = models.ForeignKey(
        Class, on_delete=models.CASCADE,
        related_name='class_subjects', verbose_name=_('Class')
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
        unique_together = ('user_class', 'school_subject')
        verbose_name = _('Class subject')
        verbose_name_plural = _('Class subjects')
        ordering = ('order', )

    @property
    def subject(self):
        return self.school_subject.subject

    def __str__(self):
        return f"{self.user_class} – {self.subject}"
