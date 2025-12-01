from django.shortcuts import render


def game_task_session_view(request, pk):

    context = {
        'user': request.user,
    }
    return render(request, 'app/dashboard/teacher/game_task/session/page.html', context)