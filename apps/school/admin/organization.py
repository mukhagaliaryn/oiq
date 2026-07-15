from django import forms
from django.contrib import admin
from unfold.admin import TabularInline
from unfold.widgets import UnfoldAdminCheckboxSelectMultipleWidget
from core.admin.base import BaseModelAdmin
from apps.school.models import Organization, Membership, OrgRole


# Organization admin
# ----------------------------------------------------------------------------------------------------------------------
# -------------- MembershipRolesFormMixin --------------
class MembershipRolesFormMixin:
    """ArrayField(roles)-ты checkbox тізіміне айналдырады (Unfold ArrayField-ті әдепкі textarea етеді)."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'roles':
            return forms.MultipleChoiceField(
                choices=OrgRole.choices,
                widget=UnfoldAdminCheckboxSelectMultipleWidget,
                required=False,
                label=db_field.verbose_name,
            )

        return super().formfield_for_dbfield(db_field, request, **kwargs)


# -------------- MembershipTabularInline --------------
class MembershipTabularInline(MembershipRolesFormMixin, TabularInline):
    model = Membership
    extra = 0
    tab = True
    autocomplete_fields = ('user',)


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
class MembershipAdmin(MembershipRolesFormMixin, BaseModelAdmin):
    list_display = ('user', 'organization', 'roles')
    search_fields = ('user__username', 'user__email', 'organization__name')
    list_filter = ('organization',)
    autocomplete_fields = ('user', 'organization')

    fieldsets = (
        (None, {'fields': ('user', 'organization', 'roles')}),
    )
