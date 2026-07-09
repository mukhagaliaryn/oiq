from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget
from core.admin.base import BaseModelAdmin, LinkedAdminMixin
from apps.catalog.models import Chapter, Subject, Topic, Question
from apps.catalog.forms.question import QuestionAdminForm


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- ChapterInline --------------
class ChapterInline(LinkedAdminMixin, TabularInline):
    model = Chapter
    extra = 0
    fields = ('order', 'title', 'grade', 'is_active', 'detail_link')
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
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }
    fieldsets = (
        (None, {'fields': ('name', 'description', 'cover', 'grades', 'order')}),
    )


# Chapter admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- TopicInline --------------
class TopicInline(LinkedAdminMixin, TabularInline):
    model = Topic
    fields = ('order', 'title', 'is_active', 'detail_link')
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
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }
    inlines = (TopicInline,)

    fieldsets = (
        (None, {'fields': ('title', 'subject', 'grade', 'description', 'admin_link')}),
    )

    def admin_link(self, obj, *args, **kwargs):
        return self.parent_link(obj, 'subject')

    admin_link.short_description = _('Subject link')


# Topic admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- QuestionInline --------------
class QuestionInline(LinkedAdminMixin, TabularInline):
    model = Question
    fields = ('text', 'format', 'variant', 'author', 'detail_link')
    readonly_fields = ('detail_link',)
    extra = 0
    form = QuestionAdminForm

    def detail_link(self, obj):
        return self.admin_link(obj, label=_('Detail link'))

    detail_link.short_description = _('Detail link')


# -------------- TopicAdmin --------------
@admin.register(Topic)
class TopicAdmin(LinkedAdminMixin, BaseModelAdmin):
    list_display = ('title', 'chapter', 'updated_at', 'is_active')
    search_fields = ('title', 'subject__name', 'chapter__title')
    readonly_fields = ('admin_link',)
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }
    inlines = (QuestionInline, )

    fieldsets = (
        (None, {'fields': ('title', 'chapter', 'description', 'admin_link')}),
    )

    def admin_link(self, obj, *args, **kwargs):
        return self.parent_link(obj, 'chapter')

    admin_link.short_description = _('Chapter link')
