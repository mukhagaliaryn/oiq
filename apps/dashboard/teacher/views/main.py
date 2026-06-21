from django.shortcuts import render
from core.utils.decorators import teacher_required


@teacher_required
def dashboard_view(request):
    return render(request,'app/dashboard/teacher/page.html')
