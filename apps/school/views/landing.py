from django.shortcuts import redirect, render
from apps.school.selectors import get_user_organizations


# -------------- landing_view --------------
def landing_view(request):
    if not request.user.is_authenticated:
        return render(request, 'school/landing.html', {'organizations': None})

    organizations = get_user_organizations(request.user)

    if organizations.count() == 1:
        return redirect('school:dashboard', org=organizations.first().slug)

    return render(request, 'school/landing.html', {'organizations': organizations})
