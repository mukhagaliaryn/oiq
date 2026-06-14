from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline, ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from core.admin import BaseModelAdmin
from core.admin.base import LinkedAdminMixin
from core.forms.content import QuestionAdminForm, OptionAdminForm
from core.models import Chapter, Subject, Topic, Question, QuestionFormat, FormatVariant, Option
from core.utils.text import question_text_preview


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
    fields = ('text', 'format', 'detail_link')
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
# -------------- OptionInline --------------
class OptionInline(TabularInline):
    model = Option
    extra = 0
    form = OptionAdminForm


# -------------- QuestionAdmin --------------
@admin.register(Question)
class QuestionAdmin(LinkedAdminMixin, BaseModelAdmin):
    list_display = ('text_preview', 'topic', 'format', 'variant', 'level', 'time_limit', 'updated_at', 'is_active')
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

    def text_preview(self, obj):
        return mark_safe(question_text_preview(obj.text))

    def admin_link(self, obj, *args, **kwargs):
        return self.parent_link(obj, 'topic')

    text_preview.short_description = _('Text')
    admin_link.short_description = _('Question link')

    class Media:
        css = {
            'all': (
                'js/oiq-question-preview/ui.css',
            )
        }
        js = (
            'js/oiq-question-preview/oiq-question-preview.bundle.js',
            'js/admin/question-format-variant.js',
        )
