from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from apps.dashboard.forms.account import TeacherAccountForm


# teacher account modal
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def account_view(request):
    if request.headers.get('HX-Request') != 'true':
        raise Http404('Page not found')

    user = request.user
    if request.method == 'POST':
        form = TeacherAccountForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Personal data saved'))
        else:
            messages.error(request, _('Something went wrong'))
    else:
        form = TeacherAccountForm(instance=user)

    context = {
        'form': form,
    }
    return render(request, 'app/dashboard/settings/account/page.html', context)


# teacher security
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def security_view(request):
    if request.headers.get('HX-Request') != 'true':
        raise Http404('Page not found')

    context = {}
    return render(request, 'app/dashboard/settings/security/page.html', context)


# teacher generics
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def generics_view(request):
    if request.headers.get('HX-Request') != 'true':
        raise Http404('Page not found')

    context = {}
    return render(request, 'app/dashboard/components/teacher_security.html', context)
