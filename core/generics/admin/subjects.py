from django.contrib import admin
from django.contrib.admin import register
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from core.generics.models import Subject, Chapter, Topic


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
# ChapterTab
class ChapterTab(admin.TabularInline):
    model = Chapter
    extra = 0
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        if obj.pk:
            url = reverse('admin:generics_chapter_change', args=[obj.pk])
            return format_html('<a href="{}">Толығырақ</a>', url)
        return '-'

    detail_link.short_description = _('Detail link')


# SubjectAdmin
@register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'order', )

    inlines = (ChapterTab, )


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
# TopicTab
class TopicTab(admin.TabularInline):
    model = Topic
    extra = 0
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        if obj.pk:
            url = reverse('admin:generics_topic_change', args=[obj.pk])
            return format_html('<a href="{}">Толығырақ</a>', url)
        return '-'

    detail_link.short_description = _('Detail link')


# ChapterAdmin
@register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'order', )
    inlines = (TopicTab, )


# Topic admin
# ----------------------------------------------------------------------------------------------------------------------
# TopicAdmin
@register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'chapter', 'order', )
