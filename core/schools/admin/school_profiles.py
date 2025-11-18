from django.contrib import admin
from django.contrib.admin import register
from core.schools.models import ClassSubject, SchoolClass, SchoolProfile


# SchoolProfile admin
# ----------------------------------------------------------------------------------------------------------------------
@register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_filter = ('school', 'email', 'website', 'rating', )


# SchoolSubject admin
# ----------------------------------------------------------------------------------------------------------------------
class ClassSubjectTab(admin.StackedInline):
    model = ClassSubject
    extra = 0
    filter_horizontal = ('teachers', )


# SchoolClassAdmin
@register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'grade', 'letter', 'school', 'homeroom_teacher', )
    list_filter = ('grade', 'letter', 'school', )
    inlines = (ClassSubjectTab, )
