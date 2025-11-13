from django.contrib import messages
from django.http import Http404
from django.shortcuts import render
from core.utils.decorators import role_required
from apps.teacher.forms.account import TeacherAccountForm


# teacher account modal
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_account_view(request):
    if request.headers.get("HX-Request") != "true":
        raise Http404("Бұл бет тек модал арқылы ашылады.")

    user = request.user

    if request.method == "POST":
        form = TeacherAccountForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт баптаулары сәтті сақталды.')
        else:
            messages.error(request, 'Формада қателер бар, қайта тексеріңіз.')
    else:
        form = TeacherAccountForm(instance=user)

    context = {
        "form": form,
    }
    return render(request, 'app/dashboard/teacher/components/teacher_account.html', context)


@role_required('teacher')
def teacher_security_view(request):
    context = {}
    return render(request, 'app/dashboard/teacher/components/teacher_security.html', context)


@role_required('teacher')
def teacher_generics_view(request):
    context = {}
    return render(request, 'app/dashboard/teacher/components/teacher_security.html', context)