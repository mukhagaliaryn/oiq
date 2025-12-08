import re

from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from apps.main.services.gameplay_session_join import get_joinable_session_by_pin, get_unique_nickname_for_session
from core.models import Participant


# gameplay_join page
# ----------------------------------------------------------------------------------------------------------------------
@require_http_methods(['GET', 'POST'])
def gameplay_join_view(request):
    if request.method == 'GET':
        token = request.session.get('current_game_participant_token')
        participant = None
        if token:
            participant = (
                Participant.objects
                .select_related('session')
                .filter(token=token)
                .first()
            )

        if participant:
            session = participant.session

            if session.is_time_over() or session.is_finished():
                request.session.pop('current_game_participant_token', None)
            else:
                if session.is_pending():
                    return redirect('main:gameplay_waiting', token=participant.token)
                if session.is_active():
                    return redirect('main:gameplay_play', token=participant.token)

                request.session.pop('current_game_participant_token', None)

        pin_prefill = (request.GET.get('pin') or '').strip()
        context = {
            'pin_prefill': pin_prefill,
            'error': None,
            'field_errors': {},
        }
        return render(request, 'app/main/gameplay/join/page.html', context)

    # -------------------- POST --------------------
    pin_code = (request.POST.get('pin') or '').strip()
    nickname = (request.POST.get('nickname') or '').strip()

    errors = {}
    if not pin_code:
        errors['pin'] = 'PIN кодты енгізіңіз.'

    if not nickname:
        errors['nickname'] = 'Есіміңізді (никнейм) енгізіңіз.'
    else:
        if len(nickname) > 20:
            errors['nickname'] = 'Есім ең көп дегенде 20 таңба болуы керек.'
        allowed_pattern = r"^[0-9A-Za-zА-Яа-яӘәІіҢңҒғҮүҰұҚқӨөЫыЁё ._'-]+$"
        if not re.match(allowed_pattern, nickname):
            errors['nickname'] = 'Есім тек әріп, цифра және қарапайым белгілерден тұруы керек.'

    if errors:
        context = {
            'pin_prefill': pin_code,
            'error': 'Деректерді дұрыс енгізіңіз.',
            'field_errors': errors,
        }
        return render(request, 'app/main/gameplay/join/page.html', context)

    session = get_joinable_session_by_pin(pin_code)
    if not session:
        context = {
            'pin_prefill': pin_code,
            'error': 'Сессия табылмады немесе басталып/аяқталып кетті.',
            'field_errors': {},
        }
        return render(request, 'app/main/gameplay/join/page.html', context)

    token = request.session.get('current_game_participant_token')
    participant = None

    if token:
        participant = Participant.objects.filter(
            token=token,
            session=session,
        ).first()

    if not participant:
        final_nickname = get_unique_nickname_for_session(session, nickname)
        participant = Participant.objects.create(
            session=session,
            nickname=final_nickname,
            started_at=timezone.now(),
        )

    request.session['current_game_participant_token'] = str(participant.token)
    return redirect('main:gameplay_waiting', token=participant.token)


# gameplay_waiting page
# ----------------------------------------------------------------------------------------------------------------------
def gameplay_waiting_view(request, token):
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
    return render(request, 'app/main/gameplay/waiting/page.html', context)


# gameplay_waiting_poll
def gameplay_waiting_poll_fragment(request, token):
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