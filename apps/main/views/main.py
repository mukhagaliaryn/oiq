from django.shortcuts import render
from core.utils.decorators import anonymous_required


# -------------- main page --------------
@anonymous_required
def main_view(request):
    context = {}
    return render(request, 'app/page.html', context)
