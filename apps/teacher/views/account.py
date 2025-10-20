from django.shortcuts import render


def teacher_profile_view(request):

    context = {}
    return render(request, 'app/dashboard/teacher/account/profile/page.html', context)