from django.contrib import admin
from django.contrib.admin import register
from core.generics.models import Subject


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
@register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'order', )
