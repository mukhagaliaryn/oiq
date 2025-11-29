from django.contrib import admin
from core.models import GameTask, GameTaskQuestion


# GameTask admin
# ----------------------------------------------------------------------------------------------------------------------
# GameTaskQuestionInline
class GameTaskQuestionInline(admin.StackedInline):
    model = GameTaskQuestion
    extra = 0


# GameTaskAdmin
@admin.register(GameTask)
class GameTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'activity', 'subject', )
    list_filter = ('owner', 'activity', 'subject', )
    search_fields = ('name', 'owner', 'activity', 'subject', )

    inlines = (GameTaskQuestionInline, )
