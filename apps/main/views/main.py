from django.shortcuts import render
from apps.accounts.decorators import anonymous_required


# -------------- main page --------------
@anonymous_required
def main_view(request):
    context = {}
    return render(request, 'main/page.html', context)
