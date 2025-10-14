from django.shortcuts import render
from core.decorators.roles import role_required


# manager dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('manager')
def manager_dashboard_view(request):

    context = {}
    return render(request, 'app/dashboard/manager/page.html', context)
