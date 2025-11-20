from django.contrib import admin
from core.generics.models import Interactive


# InteractiveAdmin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(Interactive)
class InteractiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'interactive_type', 'order', )
    list_filter = ('interactive_type', )
