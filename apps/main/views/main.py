from django.shortcuts import render, redirect, get_object_or_404
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
def game_task_session_join_view(request):
    if request.method == 'GET':
        pin_prefill = request.GET.get('pin', '').strip()
        context = {
            'pin_prefill': pin_prefill,
            'error': None
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

    return redirect('main:session_play', token=participant.token)


# game_task_session_play page
# ----------------------------------------------------------------------------------------------------------------------
def game_task_session_play_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    session = participant.session
    game_task = session.game_task

    status = session.status

    return render(request, 'app/main/play/page.html', {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'status': status,
    })
