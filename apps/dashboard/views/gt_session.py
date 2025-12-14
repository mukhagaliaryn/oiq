from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from core.models import GameTask, GameTaskSession


# game_task_session_create page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def gt_session_create_view(request, pk):
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


# get_owned_session_or_404
# ----------------------------------------------------------------------------------------------------------------------
def get_owned_session_or_404(user, pk, session_id):
    game_task = get_object_or_404(
        GameTask,
        pk=pk,
        owner=user,
        status='published',
    )
    session = get_object_or_404(
        GameTaskSession.objects.select_related('game_task'),
        pk=session_id,
        game_task=game_task,
    )
    return game_task, session


# gt_session_action
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def gt_session_action(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)

    if session.is_pending():
        url_name = 'dashboard:session_waiting'
    elif session.is_active():
        url_name = 'dashboard:session_active'
    elif session.is_finished():
        url_name = 'dashboard:session_finished'
    else:
        url_name = 'dashboard:session_waiting'

    return redirect(url_name, pk=pk, session_id=session.pk)


# game_task_session_waiting page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_task_session_waiting_view(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)
    if not session.is_pending():
        return redirect('teacher:session', pk=pk, session_id=session.pk)

    join_url = request.build_absolute_uri(f"/join/?pin={session.pin_code}")

    context = {
        'session': session,
        'game_task': game_task,
        'join_url': join_url,
    }
    return render(request, 'app/dashboard/game_tasks/game_task/session/waiting/page.html', context)


# gt_session_participants fragment
@login_required
def gt_session_participants_fragment(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)
    participants = session.participants.all().order_by('started_at', 'id')
    context = {
        'session': session,
        'participants': participants,
    }
    return render(
        request,
        'app/dashboard/game_tasks/game_task/session/waiting/_session_participants.html',
        context
    )


# gt_session_start_action
@login_required
def gt_session_start_action(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)
    if request.method != 'POST':
        return redirect('dashboard:session_waiting', pk=game_task.pk, session_id=session.pk)

    if session.is_pending():
        session.status = 'active'
        session.started_at = timezone.now()
        session.save(update_fields=['status', 'started_at'])

    return redirect('dashboard:session_active', pk=game_task.pk,  session_id=session.pk)


# game_task_session_active page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def gt_session_active_view(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)

    if not session.is_active():
        return redirect('teacher:session', pk=game_task.pk, session_id=session.pk)

    context = {
        'session': session,
        'game_task': game_task,
    }
    return render(request, 'app/dashboard/game_tasks/game_task/session/active/page.html', context)


# gt_session_active_leaderboard_fragment
@login_required
def gt_session_active_leaderboard_fragment(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)

    if not session.is_active():
        return redirect('teacher:session', pk=pk, session_id=session.pk)

    participants = (
        session.participants
        .all()
        .order_by('-score', '-correct_count', 'finished_at', 'started_at', 'pk')
    )

    context = {
        'session': session,
        'game_task': game_task,
        'participants': participants,
    }
    return render(request, 'app/dashboard/game_tasks/game_task/session/active/_leaderboard.html', context)


# gt_session_finish_action
@login_required
def gt_session_finish_action(request, pk, session_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)

    if not session.is_finished():
        session.status = 'finished'
        session.finished_at = timezone.now()
        session.save(update_fields=['status', 'finished_at'])
    return redirect('dashboard:session_finished', pk=pk, session_id=session.pk)


# game_task_session_finished page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def gt_session_finished_view(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)
    if not session.is_finished():
        return redirect('dashboard:session', pk=pk, session_id=session.pk)

    participants = (
        session.participants
        .all()
        .order_by('-score', '-correct_count', 'finished_at')
    )

    finished_count = participants.filter(is_finished=True).count()
    total = participants.count()
    avg_score = participants.aggregate(avg=Avg('score'))['avg']

    context = {
        'session': session,
        'game_task': game_task,
        'participants': participants,
        'finished_count': finished_count,
        'total_participants': total,
        'avg_score': avg_score,
    }
    return render(
        request,
        'app/dashboard/game_tasks/game_task/session/summary/page.html',
        context
    )


# game_task_delete action
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@require_POST
def gt_session_delete_action(request, pk, session_id):
    user = request.user
    game_task, session = get_owned_session_or_404(user, pk, session_id)
    session.delete()
    messages.success(request, 'Ойын тапсырмасы жойылды!')
    return redirect('dashboard:game_task_detail', pk=pk)
