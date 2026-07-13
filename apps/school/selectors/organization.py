from apps.school.models import Organization, Membership


# -------------- get_organization_by_slug --------------
def get_organization_by_slug(slug):
    return Organization.objects.filter(slug=slug, is_active=True).first()


# -------------- get_membership --------------
def get_membership(user, organization):
    if not user.is_authenticated:
        return None

    return (
        Membership.objects
        .filter(user=user, organization=organization, is_active=True)
        .select_related('user', 'organization')
        .first()
    )


# -------------- get_org_members --------------
def get_org_members(organization, role=None):
    members = (
        Membership.objects
        .filter(organization=organization, is_active=True)
        .select_related('user')
    )

    if role:
        members = members.filter(roles__contains=[role])

    return members


# -------------- get_membership_by_id --------------
def get_membership_by_id(organization, membership_id):
    return Membership.objects.filter(
        pk=membership_id, organization=organization, is_active=True,
    ).select_related('user').first()


# -------------- get_user_organizations --------------
def get_user_organizations(user):
    return (
        Organization.objects
        .filter(memberships__user=user, memberships__is_active=True, is_active=True)
        .distinct()
    )
