from django.contrib import admin
from django.contrib.admin import register
from django.utils.translation import gettext_lazy as _
from core.forms.subject import QuestionForm, OptionForm
from core.models import Subject, Chapter, Topic, Question, QuestionFormat, QuestionVariant, Option
from core.admin.mixins import LinkedAdminMixin


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
    search_fields = ('name', )
    inlines = (ChapterInline, )


# Chapter admin
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
    list_filter = ('subject', )
    search_fields = ('title', 'subject__name', )
    inlines = (TopicInline, )
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.parent_link(obj, 'subject')
    detail_link.short_description = _('Subject')


# Topic admin
# ----------------------------------------------------------------------------------------------------------------------
class QuestionInline(LinkedAdminMixin, admin.StackedInline):
    model = Question
    extra = 0
    readonly_fields = ('detail_link', )
    form = QuestionForm

    def detail_link(self, obj):
        return self.admin_link(obj, 'question', label=_('Detail view'))
    detail_link.short_description = _('Detail link')


# TopicAdmin
@register(Topic)
class TopicAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ( 'title', 'chapter', 'order', )
    list_filter = ('chapter', )
    readonly_fields = ('detail_link', )
    inlines = (QuestionInline, )

    def detail_link(self, obj):
        return self.parent_link(obj, 'chapter')
    detail_link.short_description = _('Chapter')

    class Media:
        js = ('scripts/admin/format_variant.js', )


# QuestionFormat admin
# ----------------------------------------------------------------------------------------------------------------------
# QuestionVariantInline
class QuestionVariantInline(LinkedAdminMixin, admin.TabularInline):
    model = QuestionVariant
    extra = 0


# QuestionFormatAdmin
@register(QuestionFormat)
class QuestionFormatAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'code', 'order', )
    inlines = (QuestionVariantInline, )


# Question admin
# ----------------------------------------------------------------------------------------------------------------------
# AnswerInline
class OptionInline(admin.TabularInline):
    model = Option
    extra = 0
    form = OptionForm


# QuestionAdmin
@register(Question)
class QuestionAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ( '__str__', 'format', 'variant', 'topic', )
    list_filter = ('format', 'variant', 'level', )
    readonly_fields = ('detail_link', )
    form = QuestionForm

    def detail_link(self, obj):
        return self.parent_link(obj, 'topic')
    detail_link.short_description = _('Topic')

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []

        inline_instances = []
        format_code = getattr(obj.format, 'code', None)

        if format_code == 'test':
            inline_instances.append(OptionInline(self.model, self.admin_site))

        return inline_instances

    class Media:
        js = ('scripts/admin/format_variant.js', )
