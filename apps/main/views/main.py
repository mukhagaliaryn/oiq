from django.conf import settings
from django.shortcuts import render
from apps.accounts.decorators import anonymous_required
from core.utils.urls import build_absolute_url


# -------------- main page --------------
@anonymous_required
def main_view(request):
    context = {
        'school_url': build_absolute_url(settings.SCHOOL_HOST, 'school:landing', urlconf='config.urls_school'),
    }
    return render(request, 'main/page.html', context)
