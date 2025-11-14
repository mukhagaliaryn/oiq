from django.shortcuts import render
from core.utils.decorators import role_required


# teacher dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_dashboard_view(request):
    context = {
    }
    return render(request, 'app/dashboard/teacher/page.html', context)


# teacher classes page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_classes_view(request):
    return render(request, 'app/dashboard/teacher/classes/page.html', {})


# teacher pupils page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_pupils_view(request):
    return render(request, 'app/dashboard/teacher/pupils/page.html', {})
