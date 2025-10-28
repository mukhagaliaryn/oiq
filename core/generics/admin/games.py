from django.contrib import admin
from django.contrib.admin import register
from core.generics.models import Game, Virtual


# GameAdmin
# ----------------------------------------------------------------------------------------------------------------------
@register(Game)
class GameAdmin(admin.ModelAdmin):
    list_filter = ('name', 'slug', 'order', )
    filter_horizontal = ('required_qs', )



# GameAdmin
# ----------------------------------------------------------------------------------------------------------------------
@register(Virtual)
class VirtualAdmin(admin.ModelAdmin):
    list_filter = ('name', 'slug', 'order', )
    filter_horizontal = ('required_qs', )
