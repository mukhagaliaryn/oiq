from django.db.models import Avg
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from apps.main.services.main import get_joinable_session_by_pin
from core.models import Participant


# main page
# ----------------------------------------------------------------------------------------------------------------------
def main_view(request):
    context = {}
    return render(request, 'app/main/page.html', context)


# game_task_session_join page
# ----------------------------------------------------------------------------------------------------------------------

def gt_session_join_view(request):
    if request.method == 'GET':
        current_token = request.session.get('current_game_participant_token')

        if current_token:
            participant = (
                Participant.objects
                .select_related('session')
                .filter(token=current_token)
                .first()
            )
            if participant:
                session = participant.session
                if session.is_pending():
                    return redirect('main:session_waiting', token=participant.token)
                else:
                    return redirect('main:session_play', token=participant.token)

        pin_prefill = request.GET.get('pin', '').strip()
        context = {
            'pin_prefill': pin_prefill,
            'error': None,
        }
        return render(request, 'app/main/join/page.html', context)

    pin_code = (request.POST.get('pin') or '').strip()
    nickname = (request.POST.get('nickname') or '').strip()

    errors = {}
    if not pin_code:
        errors['pin'] = 'PIN кодты енгізіңіз.'
    if not nickname:
        errors['nickname'] = 'Есіміңізді (nickname) енгізіңіз.'

    if errors:
        context = {
            'pin_prefill': pin_code,
            'error': 'Деректерді толық енгізіңіз.',
            'field_errors': errors,
        }
        return render(request, 'app/main/join/page.html', context)

    session = get_joinable_session_by_pin(pin_code)
    if not session:
        return render(request, 'app/main/join/page.html', {
            'pin_prefill': pin_code,
            'error': 'Сессия табылмады немесе басталып/аяқталып кетті.',
            'field_errors': {},
        })

    session_key = f'game_session_participant_{session.pk}'
    existing_token = request.session.get(session_key)

    if existing_token:
        participant = Participant.objects.filter(
            token=existing_token,
            session=session,
        ).first()
    else:
        participant = None

    if participant:
        pass
    else:
        participant = Participant.objects.create(
            session=session,
            nickname=nickname,
            started_at=timezone.now(),
        )
        request.session[session_key] = str(participant.token)

    request.session['current_game_participant_token'] = str(participant.token)
    return redirect('main:session_waiting', token=participant.token)


# gt_session_waiting page
# ----------------------------------------------------------------------------------------------------------------------
def gt_session_waiting_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    session = participant.session
    game_task = session.game_task
    if not session.is_pending():
        return redirect('main:session_play', token=token)

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
    }
    return render(request, 'app/main/waiting/page.html', context)


# gt_session_waiting_poll
def gt_session_waiting_poll_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session'),
        token=token,
    )
    session = participant.session

    if not session.is_pending():
        resp = HttpResponse()
        resp['HX-Redirect'] = reverse('main:session_play', kwargs={'token': token})
        return resp

    return HttpResponse(status=204)


# gt_session_play page
# ----------------------------------------------------------------------------------------------------------------------
def gt_session_play_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    session = participant.session
    game_task = session.game_task

    if session.is_pending():
        return redirect('main:session_waiting', token=token)

    status = session.status

    return render(request, 'app/main/play/page.html', {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'status': status,
    })


# gt_session_finish_participant_action
# ----------------------------------------------------------------------------------------------------------------------
def gt_session_finish_participant_action(request, token):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    participant = get_object_or_404(
        Participant.objects.select_related('session'),
        token=token,
    )
    session = participant.session

    if session.is_pending():
        return redirect('main:session_waiting', token=token)

    if not participant.is_finished:
        participant.is_finished = True
        participant.finished_at = timezone.now()
        participant.save(update_fields=['is_finished', 'finished_at'])

    return redirect('main:session_result', token=token)


# gt_session_result_view
# ----------------------------------------------------------------------------------------------------------------------
def gt_session_result_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    session = participant.session
    game_task = session.game_task

    if session.is_pending():
        return redirect('main:session_waiting', token=token)

    participants_qs = (
        session.participants
        .all()
        .order_by('-score', '-correct_count', 'finished_at')
    )

    participants = list(participants_qs)
    total = len(participants)

    position = None
    for idx, p in enumerate(participants, start=1):
        if p.pk == participant.pk:
            position = idx
            break

    finished_count = participants_qs.filter(is_finished=True).count()
    avg_score = participants_qs.aggregate(avg=Avg('score'))['avg']

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'position': position,
        'total_participants': total,
        'finished_count': finished_count,
        'avg_score': avg_score,
    }
    return render(request, 'app/main/result/page.html', context)
