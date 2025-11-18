from django.db import models
from django.utils.translation import gettext_lazy as _


# SchoolProfile model
# ----------------------------------------------------------------------------------------------------------------------
class SchoolProfile(models.Model):
    school = models.OneToOneField(
        'generics.School', on_delete=models.CASCADE,
        related_name='profile', verbose_name=_('School')
    )
    logo = models.ImageField(_('Logo'), upload_to='schools/logos/', blank=True, null=True)
    address = models.CharField(_('Address'), max_length=255, blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=32, blank=True, null=True)
    email = models.EmailField(_('Email'), blank=True, null=True)
    website = models.URLField(_('Website'), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    rating = models.DecimalField(_('Rating'), max_digits=3, decimal_places=1, default=0.0)

    class Meta:
        verbose_name = _('School profile')
        verbose_name_plural = _('School profiles')

    def __str__(self):
        return _('{} profile').format(self.school.name)


# SchoolClass model
class SchoolClass(models.Model):
    school = models.ForeignKey(
        'generics.School', on_delete=models.CASCADE, null=True,
        related_name='classes', verbose_name=_('School')
    )
    grade = models.ForeignKey(
        'generics.Class', on_delete=models.CASCADE,
        related_name='school_classes', verbose_name=_('Class')
    )
    letter = models.ForeignKey(
        'generics.Letter', on_delete=models.CASCADE,
        related_name='school_class_letters', verbose_name=_('Letter')
    )
    homeroom_teacher = models.ForeignKey(
        'generics.Teacher', on_delete=models.SET_NULL, related_name='homeroom_classes',
        null=True, blank=True, verbose_name=_('Homeroom teacher')
    )

    class Meta:
        verbose_name = _('School class')
        verbose_name_plural = _('School classes')
        ordering = ('grade', 'letter', )

    def __str__(self):
        return _('{}{} - class').format(self.grade, self.letter)

    @property
    def school_class(self):
        return _('{}{} - class').format(self.grade, self.letter)


# ClassSubject model
class ClassSubject(models.Model):
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE,
        related_name='class_subjects', verbose_name=_('School class')
    )
    subject = models.ForeignKey(
        'generics.Subject', on_delete=models.CASCADE,
        related_name='class_subjects', verbose_name=_('Subject')
    )
    teachers = models.ManyToManyField(
        'generics.Teacher', related_name='teaching_subjects', blank=True, verbose_name=_('Teachers')
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        unique_together = ('school_class', 'subject')
        verbose_name = _('Class subject')
        verbose_name_plural = _('Class subjects')
        ordering = ('school_class', 'order')

    def __str__(self):
        return _('{} ({})').format(self.subject.name, self.school_class)
