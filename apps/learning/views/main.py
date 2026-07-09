from django.shortcuts import render
from apps.accounts.decorators import learner_required


@learner_required
def dashboard_view(request):
    return render(request, 'learning/page.html')
