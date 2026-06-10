from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from core.models import School, City
from django.utils.translation import gettext_lazy as _


# City
# ----------------------------------------------------------------------------------------------------------------------
class SchoolTabularInline(TabularInline):
    model = School
    extra = 0


@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'is_active')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('General information'), {'fields': ('is_active', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = (SchoolTabularInline,)


# School
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(School)
class SchoolAdmin(ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name', 'city')
    list_filter = ('city',)

    fieldsets = (
        (None, {'fields': ('city', 'name')}),
        (_('General information'), {'fields': ('is_active', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
