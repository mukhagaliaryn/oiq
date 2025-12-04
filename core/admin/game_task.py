from django.contrib import admin
from core.models import GameTask, GameTaskQuestion, GameTaskSession


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


@admin.register(GameTaskSession)
class GameTaskSessionAdmin(admin.ModelAdmin):
    list_display = ('game_task', 'pin_code', )