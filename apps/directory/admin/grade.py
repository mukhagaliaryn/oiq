from django.contrib import admin
from core.admin.base import BaseModelAdmin
from apps.directory.models import Grade


# -------------- Grade admin --------------
@admin.register(Grade)
class GradeAdmin(BaseModelAdmin):
    list_display = ('name', 'code', 'order', )
    search_fields = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'code', 'order')}),
    )
