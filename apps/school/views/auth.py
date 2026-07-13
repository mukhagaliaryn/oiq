from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from apps.accounts.services import save_user_session
from apps.school.forms.auth import LoginForm


def _safe_next_url(request):
    next_url = request.POST.get('next') or request.GET.get('next')

    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url

    return None


# -------------- login_view --------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request) or 'school:landing')

    form = LoginForm(request=request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            save_user_session(request, user)
            messages.success(request, _('You have successfully signed in.'))
            return redirect(_safe_next_url(request) or 'school:landing')

        for error in form.non_field_errors():
            messages.error(request, error)

    context = {
        'form': form,
        'next': request.GET.get('next', ''),
    }
    return render(request, 'school/auth/login.html', context)


# -------------- logout_view --------------
def logout_view(request):
    logout(request)
    messages.success(request, _('You have been signed out.'))
    return redirect('school:login')
