from django.shortcuts import render
from core.utils.decorators import role_required


@role_required('learner')
def dashboard_view(request):
    return render(request,'app/dashboard/learner/page.html')
