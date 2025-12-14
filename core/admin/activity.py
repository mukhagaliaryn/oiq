from django.contrib import admin
from core.models import Activity


# ActivityAdmin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'activity_type', 'order', )
    list_filter = ('activity_type', )
    search_fields = ('name', 'slug', 'activity_type', )

    filter_horizontal = ('question_formats', )
