from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from core.models import GameTask, GameTaskSession
from core.utils.decorators import role_required


# game_task_session_create page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_task_session_create_view(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = request.user
    game_task = get_object_or_404(GameTask, pk=pk, owner=user, status='published')

    pending_sessions_count = GameTaskSession.objects.filter(
        game_task=game_task,
        status='pending',
    ).count()

    if pending_sessions_count >= 5:
        messages.error(
            request,
            'Сізде басталмаған (pending) сессиялар саны 5-ке жетті. '
            'Алдымен оларды бастап немесе аяқтап/жабып шығыңыз.'
        )
        return redirect('dashboard:game_task_detail', pk=game_task.pk)

    try:
        duration = int(request.POST.get('duration', 10))
    except (TypeError, ValueError):
        duration = 10

    session = GameTaskSession.objects.create(
        game_task=game_task,
        duration=duration,
        status='pending',
    )
    return redirect('dashboard:session_waiting', pk=pk, session_id=session.pk)


# game_task_session_waiting page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_task_session_waiting_view(request, pk, session_id):
    user = request.user
    game_task = get_object_or_404(GameTask, pk=pk, owner=user, status='published')
    session = get_object_or_404(
        GameTaskSession.objects.select_related('game_task'),
        pk=session_id,
        game_task=game_task
    )

    if session.is_pending():
        # return redirect('teacher:session_waiting', pk=pk, session_id=session.pk)
        pass

    join_url = request.build_absolute_uri(f"/join/?pin={session.pin_code}")

    context = {
        'session': session,
        'game_task': game_task,
        'join_url': join_url,
    }
    return render(request, 'app/dashboard/game_tasks/game_task/session/waiting/page.html', context)


@login_required
def game_task_session_participants_fragment(request, pk, session_id):
    user = request.user
    game_task = get_object_or_404(GameTask, pk=pk, owner=user, status='published')
    session = get_object_or_404(
        GameTaskSession.objects.prefetch_related('participants'),
        id=session_id,
        game_task=game_task
    )
    participants = session.participants.all().order_by('started_at', 'id')
    context = {
        'session': session,
        'participants': participants,
    }
    return render(request, 'app/dashboard/game_tasks/game_task/session/_session_participants.html', context)


@login_required
def game_task_session_start_view(request, pk, session_id):
    user = request.user
    game_task = get_object_or_404(GameTask, pk=pk, owner=user, status='published')
    session = get_object_or_404(
        GameTaskSession.objects.select_related('game_task'),
        id=session_id,
        game_task=game_task
    )

    if request.method != 'POST':
        return redirect('dashboard:session_waiting', session_id=session.pk)

    if session.is_pending():
        session.status = 'active'
        session.started_at = timezone.now()
        session.save()

    return redirect('dashboard:session_waiting', session_id=session.pk)
