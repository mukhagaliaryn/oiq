from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.accounts.selectors import find_users, get_user
from apps.school.decorators import org_role_required
from apps.school.models import OrgRole
from apps.school.selectors import get_membership_by_id, get_org_members
from apps.school.services import add_member, register_and_add_member, remove_member, update_member_roles


def _clean_roles(request):
    return [role for role in request.POST.getlist('roles') if role in OrgRole.values]


# -------------- member_list_view --------------
def member_list_view(request, org):
    return render(request, 'school/members/list.html', {
        'organization': request.organization,
        'members': get_org_members(request.organization),
        'can_manage': request.membership.has_role(OrgRole.SYS_ADMIN),
        'org_roles': OrgRole.choices,
    })


# -------------- member_search_view (HTMX) --------------
@org_role_required(OrgRole.SYS_ADMIN)
def member_search_view(request, org):
    query = request.GET.get('q', '').strip()

    return render(request, 'school/members/_search_results.html', {
        'organization': request.organization,
        'query': query,
        'users': find_users(query) if query else [],
        'org_roles': OrgRole.choices,
    })


# -------------- member_add_view --------------
@org_role_required(OrgRole.SYS_ADMIN)
def member_add_view(request, org):
    user = get_user(request.POST.get('user_id'))

    if not user:
        messages.error(request, _('User not found.'))
        return redirect(reverse('school:member-list', kwargs={'org': org}))

    add_member(request.organization, user, _clean_roles(request))
    messages.success(request, _('Member added.'))

    return redirect(reverse('school:member-list', kwargs={'org': org}))


# -------------- member_register_view --------------
@org_role_required(OrgRole.SYS_ADMIN)
def member_register_view(request, org):
    email = request.POST.get('email', '').strip()

    if not email:
        messages.error(request, _('Email is required.'))
        return redirect(reverse('school:member-list', kwargs={'org': org}))

    register_and_add_member(
        organization=request.organization,
        roles=_clean_roles(request),
        email=email,
        first_name=request.POST.get('first_name', '').strip(),
        last_name=request.POST.get('last_name', '').strip(),
    )
    messages.success(request, _('Teacher registered and added.'))

    return redirect(reverse('school:member-list', kwargs={'org': org}))


# -------------- member_update_roles_view --------------
@org_role_required(OrgRole.SYS_ADMIN)
def member_update_roles_view(request, org, membership_id):
    membership = get_membership_by_id(request.organization, membership_id)

    if membership:
        update_member_roles(membership, _clean_roles(request))
        messages.success(request, _('Roles updated.'))

    return redirect(reverse('school:member-list', kwargs={'org': org}))


# -------------- member_remove_view --------------
@org_role_required(OrgRole.SYS_ADMIN)
def member_remove_view(request, org, membership_id):
    membership = get_membership_by_id(request.organization, membership_id)

    if membership:
        remove_member(membership)
        messages.success(request, _('Member removed.'))

    return redirect(reverse('school:member-list', kwargs={'org': org}))
