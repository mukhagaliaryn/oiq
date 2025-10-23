from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from core.generics.models import User, Learner, Teacher, Manager


# User admin
# ----------------------------------------------------------------------------------------------------------------------
# LearnerTab
class LearnerTab(admin.TabularInline):
    model = Learner
    extra = 0
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        if obj.pk:
            url = reverse('admin:generics_learner_change', args=[obj.pk])
            return format_html('<a href="{}">Толығырақ</a>', url)
        return '-'

    detail_link.short_description = _('Detail link')


# TeacherTab
class TeacherTab(admin.TabularInline):
    model = Teacher
    extra = 0
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        if obj.pk:
            url = reverse('admin:generics_teacher_change', args=[obj.pk])
            return format_html('<a href="{}">Толығырақ</a>', url)
        return '-'

    detail_link.short_description = _('Detail link')


# ManagerTab
class ManagerTab(admin.TabularInline):
    model = Manager
    extra = 0
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        if obj.pk:
            url = reverse('admin:generics_manager_change', args=[obj.pk])
            return format_html('<a href="{}">Толығырақ</a>', url)
        return '-'

    detail_link.short_description = _('Detail link')


# UserAdmin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser', )
    list_filter = ('is_active', 'is_staff', 'is_superuser', )
    fieldsets = (
        (
            None, {
                'fields': ('username', 'email', 'avatar', 'google_avatar', 'password')
            }
        ),
        (
            _('Personal data'), {
                'fields': ('first_name', 'last_name', 'role', )
            }
        ),
        (
            _('Permissions'), {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'last_login', ) # 'user_permissions',
            }
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide', ),
                'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', ),
            },
        ),
    )
    # filter_horizontal = ('user_permissions', )


# registrations
# ----------------------------------------------------------------------------------------------------------------------
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
