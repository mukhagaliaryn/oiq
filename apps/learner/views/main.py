from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# learner home page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def learner_home_view(request):
    context = {}
    return render(request, 'app/dashboard/learner/page.html', context)


# learner game page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def learner_games_view(request):
    context = {}
    return render(request, 'app/dashboard/learner/games/page.html', context)
