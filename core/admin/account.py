from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import UserCreationForm, AdminPasswordChangeForm
from core.models import UserRole, UserSession, User, Role


# Role admin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    prepopulated_fields = {
        'code': ('name',),
    }
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)


# User admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- UserRoleInline --------------
class UserRoleInline(TabularInline):
    model = UserRole
    extra = 0
    max_num = 1
    can_delete = True
    tab = True
    fields = ('role', 'is_system', 'is_active', 'created_at')
    readonly_fields = ('created_at',)


# -------------- UserSessionInline --------------
class UserSessionInline(TabularInline):
    model = UserSession
    extra = 0
    can_delete = False
    tab = True
    fields = ('device_type', 'device_name', 'browser', 'os', 'ip_address', 'last_activity_at')
    readonly_fields = ('device_type', 'device_name', 'browser', 'os', 'ip_address', 'user_agent', 'session_key', 'last_activity_at')

    def has_add_permission(self, request, obj=None):
        return False


# -------------- UserAdmin --------------
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('avatar_preview', 'display_name', 'username', 'email', 'role_column', 'is_verified', 'is_active', 'last_login')
    list_display_links = ('avatar_preview', 'display_name', 'username')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'user_role__role')
    search_fields = ('username', 'first_name', 'middle_name', 'last_name', 'email', 'phone')
    ordering = ('id',)
    readonly_fields = ('password_change_link', 'last_login', 'date_joined')
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    inlines = (UserRoleInline, UserSessionInline)

    fieldsets = (
        (_('Account'), {
            'classes': ('tab',),
            'fields': ('avatar', 'username', 'password', 'password_change_link'),
        }),
        (_('Personal information'), {
            'classes': ('tab',),
            'fields': ('first_name', 'middle_name', 'last_name', 'email', 'phone',
            ),
        }),
        (_('Status'), {
            'classes': ('tab',),
            'fields': ('is_verified', 'is_active',
            ),
        }),
        (_('Permissions'), {
            'classes': ('tab',),
            'fields': ('is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {
            'classes': ('tab',),
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (_('Create user'), {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active'),
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:9999px;" />',
                obj.avatar.url,
            )

        return format_html(
            '<div style="width:40px;height:40px;border-radius:9999px;background:#e5e7eb;display:flex;align-items:center;justify-content:center;font-weight:700;color:#6b7280;">{}</div>',
            (obj.username[:1] or '?').upper(),
        )

    def role_column(self, obj):
        role = obj.role
        if not role:
            return '-'

        if role.is_system:
            return format_html(
                '<span style="font-weight:600;color:#4f46e5;">{}</span>',
                role.name,
            )
        return role.name

    def password_change_link(self, obj):
        if not obj or not obj.pk:
            return '-'

        return format_html(
            '<a href="../password/" style="font-weight:600;color:#4f46e5;">{}</a>',
            _('Password change link'),
        )

    avatar_preview.short_description = _('Avatar')
    role_column.short_description = _('Role')
    password_change_link.short_description = _('Password change')


# -------------- UserRoleAdmin --------------
@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'role__name', 'role__code')
    autocomplete_fields = ('user', 'role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('user',)


# -------------- UserSessionAdmin --------------
@admin.register(UserSession)
class UserSessionAdmin(ModelAdmin):
    list_display = ('user', 'device_type', 'device_name', 'browser', 'os', 'ip_address', 'last_activity_at')
    list_filter = ('device_type', 'browser', 'os')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'device_name', 'browser', 'os', 'ip_address', 'user_agent')
    readonly_fields = ('user', 'session_key', 'device_type', 'device_name', 'browser', 'os', 'ip_address', 'user_agent', 'last_activity_at')
    ordering = ('-last_activity_at',)

    def has_add_permission(self, request):
        return False


# ----------------------------------------------------------------------------------------------------------------------
admin.site.unregister(Group)
