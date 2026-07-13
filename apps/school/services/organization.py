from django.utils.text import slugify
from apps.accounts.services import create_external_user
from apps.school.models import Organization, Membership


# -------------- generate_org_slug --------------
def generate_org_slug(name):
    slug = slugify(name)

    if not Organization.objects.filter(slug=slug).exists():
        return slug

    index = 2
    while Organization.objects.filter(slug=f'{slug}-{index}').exists():
        index += 1

    return f'{slug}-{index}'


# -------------- create_organization --------------
def create_organization(*, name, school=None, slug=None):
    organization = Organization.objects.create(
        name=name,
        school=school,
        slug=slug or generate_org_slug(name),
    )

    return organization


# -------------- add_member --------------
def add_member(organization, user, roles):
    membership, created = Membership.objects.update_or_create(
        organization=organization,
        user=user,
        defaults={'roles': roles, 'is_active': True},
    )

    return membership


# -------------- update_member_roles --------------
def update_member_roles(membership, roles):
    membership.roles = roles
    membership.save(update_fields=['roles'])

    return membership


# -------------- register_and_add_member --------------
def register_and_add_member(*, organization, roles, email, first_name='', last_name=''):
    """
    Табылмаған қолданушыны жаңа school_user (account_type) ретінде тіркеп, дереу мүше етіп қосады.
    Ұйымдағы нақты рөл (директор/мұғалім/оқушы...) — roles (Membership.roles), account_type емес.
    """
    user = create_external_user(
        email=email, first_name=first_name, last_name=last_name, account_type='school_user',
    )

    return add_member(organization, user, roles)


# -------------- remove_member --------------
def remove_member(membership):
    membership.is_active = False
    membership.save(update_fields=['is_active'])

    return membership
