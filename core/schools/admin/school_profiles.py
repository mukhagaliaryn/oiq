from django.contrib import admin
from django.contrib.admin import register
from core.schools.models import ClassSubject, SchoolClass, SchoolProfile


# SchoolProfile admin
# ----------------------------------------------------------------------------------------------------------------------
class SchoolClassInline(admin.TabularInline):
    model = SchoolClass
    extra = 0


@register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_filter = ('school', 'email', 'website', 'rating', )
    inlines = (SchoolClassInline, )


# SchoolSubject admin
# ----------------------------------------------------------------------------------------------------------------------
class ClassSubjectTab(admin.StackedInline):
    model = ClassSubject
    extra = 0
    filter_horizontal = ('teachers', )


# SchoolClassAdmin
@register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('school_profile', 'grade', 'homeroom_teacher', )
    list_filter = ('school_profile', 'grade', )
    inlines = (ClassSubjectTab, )
