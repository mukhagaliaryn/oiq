from django.contrib import admin
from django.contrib.admin import register
from core.generics.models import School, Class, Letter


# School admin
# ----------------------------------------------------------------------------------------------------------------------
@register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_type', )
    list_filter = ('school_type', )
    search_fields = ('name', )


# Class admin
# ----------------------------------------------------------------------------------------------------------------------
# LetterTab
class LetterInline(admin.TabularInline):
    model = Letter
    extra = 0


# ClassAdmin
@register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('grade', )
    search_fields = ('grade', )
    inlines = (LetterInline, )
