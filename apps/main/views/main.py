from django.shortcuts import render


# -------------- main page --------------
def main_view(request):
    context = {}
    return render(request, 'app/page.html', context)
