from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# main page
# ----------------------------------------------------------------------------------------------------------------------
def main_view(request):
    if request.user.is_authenticated:
        return redirect('learner_home')

    return render(request, 'app/page.html', {})
