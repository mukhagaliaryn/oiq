from django.contrib import admin
from unfold.admin import TabularInline
from core.admin.base import BaseModelAdmin
from apps.school.models import Organization, Membership


# Organization admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- MembershipTabularInline --------------
class MembershipTabularInline(TabularInline):
    model = Membership
    extra = 0
    tab = True


# -------------- OrganizationAdmin --------------
@admin.register(Organization)
class OrganizationAdmin(BaseModelAdmin):
    list_display = ('name', 'slug', 'school')
    search_fields = ('name', 'slug')
    list_filter = ('school',)
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'school')}),
    )
    inlines = (MembershipTabularInline,)


# Membership admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- MembershipAdmin --------------
@admin.register(Membership)
class MembershipAdmin(BaseModelAdmin):
    list_display = ('user', 'organization', 'roles')
    search_fields = ('user__username', 'user__email', 'organization__name')
    list_filter = ('organization',)

    fieldsets = (
        (None, {'fields': ('user', 'organization', 'roles')}),
    )
