from django.shortcuts import render
from apps.school.models import OrgRole


# -------------- dashboard_view --------------
def dashboard_view(request, org):
    # OrganizationMiddleware мүшелікті растап, request.organization/request.membership-ті қойған
    return render(request, 'school/workspace/dashboard.html', {
        'organization': request.organization,
        'membership': request.membership,
        'can_manage': request.membership.has_role(OrgRole.SYS_ADMIN),
    })
