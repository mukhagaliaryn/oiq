from django.contrib import admin
from django.contrib.admin import register
from core.generics.models import School, Class, Letter


# School admin
# ----------------------------------------------------------------------------------------------------------------------
@register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_type', 'order', )
    list_filter = ('school_type', )
    search_fields = ('name', )


# Class admin
# ----------------------------------------------------------------------------------------------------------------------
# ClassAdmin
@register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('grade', )
    search_fields = ('grade', )


# ClassAdmin
@register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('name', )
