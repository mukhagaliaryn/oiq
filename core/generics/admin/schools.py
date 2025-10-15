from django.contrib import admin
from django.contrib.admin import register
from core.generics.models import School, ClassType, Class, SchoolClass, ClassSubject, SchoolSubject


# School admin
# ----------------------------------------------------------------------------------------------------------------------
@register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_type', 'address', )
    list_filter = ('school_type', )
    search_fields = ('name', 'address', )


# Class admin
# ----------------------------------------------------------------------------------------------------------------------
# ClassType admin
@register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('letter', 'order', )


# ClassAdmin
@register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('grade', 'class_type', )
    list_filter = ('class_type', )
    search_fields = ('grade', )


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
