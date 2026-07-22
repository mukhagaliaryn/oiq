from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext
from apps.accounts.decorators import teacher_required


@teacher_required
def dashboard_view(request):
    hour = timezone.localtime().hour
    if hour < 12:
        greeting = gettext('Good morning')
    elif hour < 18:
        greeting = gettext('Good afternoon')
    else:
        greeting = gettext('Good evening')

    return render(request, 'teaching/page.html', {'greeting': greeting})
