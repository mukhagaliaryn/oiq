from django.contrib import admin
from django.contrib.admin import register
from core.generics.models import School, ClassType, Class, SchoolSubject, ClassSubject


# School admin
# ----------------------------------------------------------------------------------------------------------------------
class ClassTypeTab(admin.TabularInline):
    model = ClassType
    extra = 0


class ClassTab(admin.TabularInline):
    model = Class
    extra = 0


@register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_type', 'address', )
    list_filter = ('school_type', )
    search_fields = ('name', 'address', )
    inlines = (ClassTypeTab, ClassTab, )


# ClassType admin
# ----------------------------------------------------------------------------------------------------------------------
@register(ClassType)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('letter', 'order', )


# Class admin
# ----------------------------------------------------------------------------------------------------------------------
@register(Class)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('school', 'grade', 'class_type', )
    list_filter = ('school', 'class_type', )
    search_fields = ('grade', )


# SchoolSubject admin
# ----------------------------------------------------------------------------------------------------------------------
class ClassSubjectTab(admin.TabularInline):
    model = ClassSubject
    extra = 0
    filter_horizontal = ('teachers', )


# SchoolSubjectAdmin
@register(SchoolSubject)
class SchoolSubjectAdmin(admin.ModelAdmin):
    list_display = ('school', 'subject', 'order', )
    list_filter = ('school', 'subject', )
    search_fields = ('school', 'subject', )

    inlines = (ClassSubjectTab, )


# ClassSubject admin
# ----------------------------------------------------------------------------------------------------------------------
@register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('school_subject', 'user_class', 'order', )
    list_filter = ('school_subject', 'user_class', )
    filter_horizontal = ('teachers', )
