from django.contrib import messages
from django.http import Http404
from django.shortcuts import render
from core.utils.decorators import role_required
from apps.teacher.forms.account import TeacherAccountForm
from django.utils.translation import gettext_lazy as _


# teacher account modal
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
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
    return render(request, 'app/dashboard/teacher/settings/account/page.html', context)


# teacher security
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def security_view(request):
    if request.headers.get('HX-Request') != 'true':
        raise Http404('Page not found')

    context = {}
    return render(request, 'app/dashboard/teacher/settings/security/page.html', context)


# teacher generics
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def generics_view(request):
    if request.headers.get('HX-Request') != 'true':
        raise Http404('Page not found')

    context = {}
    return render(request, 'app/dashboard/teacher/components/teacher_security.html', context)
