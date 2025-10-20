from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from core.generics.models import User


# User admin
# ----------------------------------------------------------------------------------------------------------------------
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
                'fields': ('first_name', 'last_name', 'role', 'school', 'user_class', )
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
