from django.contrib import admin
from django.contrib.admin import register
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from core.models import User


# User admin
# ----------------------------------------------------------------------------------------------------------------------
# UserAdmin
@register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_role', 'is_staff', 'is_superuser', )
    list_filter = ('user_role', 'is_active', 'is_staff', 'is_superuser', )
    fieldsets = (
        (
            None, {
                'fields': ('username', 'email', 'avatar', 'password')
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


# registrations
admin.site.unregister(Group)