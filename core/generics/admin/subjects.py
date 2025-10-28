from django.contrib import admin
from django.contrib.admin import register
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from core.generics.models import Subject, Chapter, Topic, Question, TaskType, Option
from core.generics.admin.mixins import LinkedAdminMixin


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
# ChapterInline
class ChapterInline(LinkedAdminMixin, admin.TabularInline):
    model = Chapter
    extra = 0
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return self.admin_link(obj, 'chapter', label=_('Detail view'))
    detail_link.short_description = _('Detail link')


# SubjectAdmin
@register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'order', )

    inlines = (ChapterInline, )


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
# TopicInline
class TopicInline(LinkedAdminMixin, admin.TabularInline):
    model = Topic
    extra = 0
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.admin_link(obj, 'topic', label=_('Detail view'))
    detail_link.short_description = _('Detail link')


# ChapterAdmin
@register(Chapter)
class ChapterAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ( 'title', 'order', )
    inlines = (TopicInline, )
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.parent_link(obj, 'subject')
    detail_link.short_description = _('Subject')


# Topic admin
# ----------------------------------------------------------------------------------------------------------------------
class QuestionInline(LinkedAdminMixin, admin.TabularInline):
    model = Question
    exclude = ('body', )
    extra = 0
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.admin_link(obj, 'question', label=_('Detail view'))
    detail_link.short_description = _('Detail link')


# TopicAdmin
@register(Topic)
class TopicAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ( 'title', 'chapter', 'order', )
    inlines = (QuestionInline, )
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.parent_link(obj, 'chapter')
    detail_link.short_description = _('Chapter')


# Question admin
# ----------------------------------------------------------------------------------------------------------------------
# QuestionTypeAdmin
@register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_filter = ('name', 'slug', 'order', )


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


# QuestionAdmin
@register(Question)
class QuestionAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_filter = ('title', 'topic', 'task_type', 'level', )
    readonly_fields = ('detail_link', )
    inlines = (OptionInline, )

    def detail_link(self, obj):
        return self.parent_link(obj, 'topic')
    detail_link.short_description = _('Topic')
