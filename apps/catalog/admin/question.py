from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline, ModelAdmin
from core.admin.base import BaseModelAdmin, LinkedAdminMixin
from core.utils.text import question_text_preview
from apps.catalog.models import QuestionFormat, FormatVariant, Question, Option
from apps.catalog.forms.question import QuestionAdminForm, OptionAdminForm


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
    list_display = ('text_preview', 'topic', 'author', 'format', 'variant', 'level', 'time_limit', 'updated_at', 'is_active')
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
            'fields': ('format', 'variant', 'level', 'time_limit', 'author')
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
