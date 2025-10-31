from django.contrib import admin
from django.contrib.admin import register
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from core.generics.admin.mixins import LinkedAdminMixin
from core.generics.models import User, Learner, Teacher, Manager


# User admin
# ----------------------------------------------------------------------------------------------------------------------
# LearnerTab
class LearnerInline(admin.TabularInline):
    model = Learner
    extra = 0


# TeacherTab
class TeacherInline(LinkedAdminMixin, admin.StackedInline):
    model = Teacher
    extra = 0
    filter_horizontal = ('subjects', )
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return self.admin_link(obj, 'teacher', label=_('Detail view'))
    detail_link.short_description = _('Detail link')


# ManagerTab
class ManagerInline(admin.StackedInline):
    model = Manager
    extra = 0


# UserAdmin
@register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_role', 'is_staff', 'is_superuser', )
    list_filter = ('user_role', 'is_active', 'is_staff', 'is_superuser', )
    fieldsets = (
        (
            None, {
                'fields': ('username', 'email', 'avatar', 'google_avatar', 'password')
            }
        ),
        (
            _('Personal data'), {
                'fields': ('first_name', 'last_name', 'user_role', )
            }
        ),
        (
            _('Permissions'), {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'last_login', )
            }
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide', ),
                'fields': ('email', 'username', 'first_name', 'last_name', 'user_role', 'password1', 'password2', ),
            },
        ),
    )

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if not obj:
            return []

        role = getattr(obj, 'user_role', None)

        if role == 'learner':
            inlines = [LearnerInline(self.model, self.admin_site)]
        elif role == 'teacher':
            inlines = [TeacherInline(self.model, self.admin_site)]
        elif role == 'manager':
            inlines = [ManagerInline(self.model, self.admin_site)]

        return inlines


# Teacher admin
# ----------------------------------------------------------------------------------------------------------------------
# TeacherAdmin
@register(Teacher)
class TeacherAdmin(LinkedAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'school', 'is_homeroom_teacher', )
    filter_horizontal = ('subjects', )
    readonly_fields = ('detail_link', )

    def detail_link(self, obj):
        return self.parent_link(obj, 'user')
    detail_link.short_description = _('User')


# registrations
admin.site.unregister(Group)
