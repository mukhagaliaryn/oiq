from django.contrib import admin
from unfold.admin import TabularInline
from core.admin.base import BaseModelAdmin
from apps.directory.models import City, School


# City admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- SchoolTabularInline --------------
class SchoolTabularInline(TabularInline):
    model = School
    extra = 0
    tab = True


# -------------- CityAdmin --------------
@admin.register(City)
class CityAdmin(BaseModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'is_active')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
    )
    inlines = (SchoolTabularInline,)


# School admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- School admin --------------
@admin.register(School)
class SchoolAdmin(BaseModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name', 'city')
    list_filter = ('city',)

    fieldsets = (
        (None, {'fields': ('name', 'city')}),
    )
