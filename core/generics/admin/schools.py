from django.contrib import admin
from django.contrib.admin import register
from core.generics.models import School, Class, SchoolClass, ClassSubject, SchoolSubject, Letter


# School admin
# ----------------------------------------------------------------------------------------------------------------------
@register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_type', 'address', )
    list_filter = ('school_type', )
    search_fields = ('name', 'address', )


# Class admin
# ----------------------------------------------------------------------------------------------------------------------
# LetterTab
class LetterTab(admin.TabularInline):
    model = Letter
    extra = 0


# ClassAdmin
@register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('grade', )
    search_fields = ('grade', )
    inlines = (LetterTab, )


# SchoolSubject admin
# ----------------------------------------------------------------------------------------------------------------------
class ClassSubjectTab(admin.TabularInline):
    model = ClassSubject
    exclude = ('teachers', )
    extra = 0


# SchoolClassAdmin
@register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('school', 'user_class', 'homeroom_teacher', )
    list_filter = ('school', 'user_class', )
    inlines = (ClassSubjectTab, )


# ClassSubject admin
# ----------------------------------------------------------------------------------------------------------------------
@register(SchoolSubject)
class SchoolSubjectAdmin(admin.ModelAdmin):
    list_display = ('school', 'subject', 'order', )
    list_filter = ('school', 'subject', )
