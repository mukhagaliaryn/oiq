from django.shortcuts import render

from core.decorators.roles import role_required


# teacher dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_dashboard_view(request):

    context = {}
    return render(request, 'app/dashboard/teacher/page.html', context)