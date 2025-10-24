from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from core.generics.admin.mixins import LinkedAdminMixin
from core.generics.models import User, Learner, Teacher, Manager


# User admin
# ----------------------------------------------------------------------------------------------------------------------
# LearnerTab
class LearnerTab(admin.StackedInline):
    model = Learner
    extra = 0


# TeacherTab
class TeacherTab(admin.StackedInline):
    model = Teacher
    extra = 0
    filter_horizontal = ('subjects', )


# ManagerTab
class ManagerTab(admin.StackedInline):
    model = Manager
    extra = 0


# UserAdmin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_role', 'is_staff', 'is_superuser', )
    list_filter = ('is_active', 'is_staff', 'is_superuser', )
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
                'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', ),
            },
        ),
    )

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if not obj:
            return []  # жаңа қолданушы қосқанда ешқандай inline шықпайды

        role = getattr(obj, 'user_role', None)

        if role == 'learner':
            inlines = [LearnerTab(self.model, self.admin_site)]
        elif role == 'teacher':
            inlines = [TeacherTab(self.model, self.admin_site)]
        elif role == 'manager':
            inlines = [ManagerTab(self.model, self.admin_site)]

        return inlines


# registrations
# ----------------------------------------------------------------------------------------------------------------------
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
