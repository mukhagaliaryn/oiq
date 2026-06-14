from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline, ModelAdmin
from core.admin import BaseModelAdmin
from core.admin.base import LinkedAdminMixin
from core.forms.content import QuestionAdminForm
from core.models import Chapter, Subject, Topic, Question, QuestionFormat, FormatVariant, Option


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- ChapterInline --------------
class ChapterInline(LinkedAdminMixin, TabularInline):
    model = Chapter
    extra = 0
    fields = ('title', 'grade', 'order', 'detail_link')
    ordering = ('order',)
    tab = True
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return self.admin_link(obj, label=_('Detail link'))

    detail_link.short_description = _('Detail link')


# -------------- SubjectAdmin --------------
@admin.register(Subject)
class SubjectAdmin(BaseModelAdmin):
    list_display = ('name', 'order', 'updated_at', 'is_active')
    search_fields = ('name',)
    ordering = ('order',)
    inlines = (ChapterInline,)
    filter_horizontal = ('grades',)

    fieldsets = (
        (None, {'fields': ('name', 'description', 'cover', 'grades', 'order')}),
    )


# Chapter admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- TopicInline --------------
class TopicInline(LinkedAdminMixin, TabularInline):
    model = Topic
    fields = ('title', 'order', 'detail_link')
    extra = 0
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return self.admin_link(obj, label=_('Detail link'))

    detail_link.short_description = _('Detail link')


# -------------- ChapterAdmin --------------
@admin.register(Chapter)
class ChapterAdmin(LinkedAdminMixin, BaseModelAdmin):
    list_display = ('title', 'subject', 'grade', 'updated_at', 'is_active')
    search_fields = ('title', 'subject__name', 'grade__title')
    list_filter = ('subject', 'grade',)
    readonly_fields = ('admin_link',)

    inlines = (TopicInline,)

    fieldsets = (
        (None, {'fields': ('title', 'subject', 'grade', 'description', 'admin_link')}),
    )

    def admin_link(self, obj, *args, **kwargs):
        return self.parent_link(obj, 'subject')

    admin_link.short_description = _('Subject link')


# Topic admin
# ----------------------------------------------------------------------------------------------------------------------
class QuestionInline(LinkedAdminMixin, TabularInline):
    model = Question
    fields = ('text', 'format', 'detail_link')
    readonly_fields = ('detail_link',)
    extra = 0

    def detail_link(self, obj):
        return self.admin_link(obj, label=_('Detail link'))

    detail_link.short_description = _('Detail link')


# -------------- TopicAdmin --------------
@admin.register(Topic)
class TopicAdmin(LinkedAdminMixin, BaseModelAdmin):
    list_display = ('title', 'chapter', 'updated_at', 'is_active')
    search_fields = ('title', 'subject__name', 'chapter__title')
    readonly_fields = ('admin_link',)
    inlines = (QuestionInline, )

    fieldsets = (
        (None, {'fields': ('title', 'chapter', 'description', 'admin_link')}),
    )

    def admin_link(self, obj, *args, **kwargs):
        return self.parent_link(obj, 'chapter')

    admin_link.short_description = _('Chapter link')



# Question format admin
# ----------------------------------------------------------------------------------------------------------------------
class FormatVariantInline(TabularInline):
    model = FormatVariant
    extra = 0


# -------------- QuestionFormatAdmin --------------
@admin.register(QuestionFormat)
class QuestionFormatAdmin(ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)
    inlines = (FormatVariantInline,)


# Question admin
# ----------------------------------------------------------------------------------------------------------------------
class OptionInline(TabularInline):
    model = Option
    extra = 0



# -------------- QuestionAdmin --------------
@admin.register(Question)
class QuestionAdmin(LinkedAdminMixin, BaseModelAdmin):
    list_display = ('text', 'topic', 'format', 'variant', 'level', 'time_limit', 'updated_at', 'is_active')
    search_fields = ('text', 'topic__name', 'format__name', 'variant__name')
    list_filter = ('topic', 'format', 'variant', 'level')
    form = QuestionAdminForm
    readonly_fields = ('admin_link',)
    inlines = (OptionInline, )

    fieldsets = (
        (_('Question content'), {
            'fields': ('text', 'topic', 'admin_link')
        }),
        (_('Question settings'), {
            'fields': ('format', 'variant', 'level', 'time_limit')
        }),
    )

    def admin_link(self, obj, *args, **kwargs):
        return self.parent_link(obj, 'topic')
