from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.decorators.roles import role_required


# learner home page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('pupil')
def learner_home_view(request):
    context = {}
    return render(request, 'app/dashboard/learner/page.html', context)


# learner game page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('pupil')
def learner_games_view(request):
    context = {}
    return render(request, 'app/dashboard/learner/games/page.html', context)
