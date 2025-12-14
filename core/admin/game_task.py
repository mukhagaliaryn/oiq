from django.contrib import admin
from core.admin import LinkedAdminMixin
from core.models import GameTask, GameTaskQuestion, GameTaskSession, Participant, QuestionAttempt, TestAnswer
from django.utils.translation import gettext_lazy as _


# GameTask admin
# ----------------------------------------------------------------------------------------------------------------------
# GameTaskQuestionInline
class GameTaskQuestionInline(admin.TabularInline):
    model = GameTaskQuestion
    extra = 0


# GameTaskSessionInline
class GameTaskSessionInline(LinkedAdminMixin, admin.StackedInline):
    model = GameTaskSession
    extra = 0
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return self.admin_link(obj, 'gametasksession', label=_('Detail view'))
    detail_link.short_description = _('Game Task Session')


# GameTaskAdmin
@admin.register(GameTask)
class GameTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'activity', 'subject', )
    list_filter = ('owner', 'activity', 'subject', )
    search_fields = ('name', 'owner__first_name', 'owner__last_name', 'activity__name', 'subject__name', )
    inlines = (GameTaskQuestionInline, GameTaskSessionInline, )


# GameTaskSession admin
# ----------------------------------------------------------------------------------------------------------------------
# ParticipantInline
class ParticipantInline(LinkedAdminMixin, admin.StackedInline):
    model = Participant
    exclude = ('current_question_id', 'current_started_at', )
    extra = 0
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.admin_link(obj, 'participant', label=_('Detail view'))
    detail_link.short_description = _('Participant')


# GameTaskSessionAdmin
@admin.register(GameTaskSession)
class GameTaskSessionAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ('pin_code', 'game_task', 'status', 'started_at', 'finished_at', 'duration', )
    list_filter = ('game_task', 'status', )
    search_fields = ('pin_code', 'game_task__name', 'status', )
    readonly_fields = ('parent_detail_link', )

    def parent_detail_link(self, obj):
        return self.parent_link(obj, 'game_task')
    parent_detail_link.short_description = _('Game Task')

    inlines = (ParticipantInline, )


# Participant admin
# ----------------------------------------------------------------------------------------------------------------------
# QuestionAttemptInline
class QuestionAttemptInline(LinkedAdminMixin, admin.TabularInline):
    model = QuestionAttempt
    extra = 0
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.admin_link(obj, 'questionattempt', label=_('Detail view'))
    detail_link.short_description = _('Question')


# ParticipantAdmin
@admin.register(Participant)
class ParticipantAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ('nickname', 'token', 'session', 'started_at', 'finished_at', )
    list_filter = ('session', )
    search_fields = ('nickname', 'session__game_task__name', 'token', )
    readonly_fields = ('parent_detail_link', )

    def parent_detail_link(self, obj):
        return self.parent_link(obj, 'session')
    parent_detail_link.short_description = _('Game Task Session')

    inlines = (QuestionAttemptInline, )


# QuestionAttempt
# ----------------------------------------------------------------------------------------------------------------------
# TestAnswerInline
class TestAnswerInline(admin.StackedInline):
    model = TestAnswer
    extra = 0
    filter_horizontal = ('selected_options', )


# QuestionAttemptAdmin
@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ('participant', 'question', 'is_correct', 'score', 'time_spent', )
    list_filter = ('participant', )
    readonly_fields = ('parent_detail_link', )

    def parent_detail_link(self, obj):
        return self.parent_link(obj, 'participant')
    parent_detail_link.short_description = _('Participant')

    inlines = (TestAnswerInline, )
