from django.shortcuts import render
from apps.accounts.decorators import teacher_required


@teacher_required
def dashboard_view(request):
    return render(request, 'teaching/page.html')
