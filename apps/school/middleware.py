from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from apps.school.selectors import get_organization_by_slug, get_membership


class OrganizationMiddleware:
    """
    <slug:org> URL кесіндісінен Organization-ды тауып request-ке қояды, мүшелікті тексереді.
    HostURLConfMiddleware-ден және AuthenticationMiddleware-ден КЕЙІН тұруы керек
    (request.urlconf/request.user-ге тәуелді). view_kwargs-та 'org' болмаса — өтеді (landing беттер).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.membership = None
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        org_slug = view_kwargs.get('org')
        if not org_slug:
            return None

        organization = get_organization_by_slug(org_slug)
        if organization is None:
            raise Http404

        if not request.user.is_authenticated:
            # school.oiq.kz-тің өз login беті — локал, cross-host редирект керек емес (school:login).
            return redirect(f"{reverse('school:login')}?next={request.get_full_path()}")

        membership = get_membership(request.user, organization)
        if membership is None:
            raise Http404

        request.organization = organization
        request.membership = membership
        return None
