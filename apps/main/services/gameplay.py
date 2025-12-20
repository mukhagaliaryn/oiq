from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from core.models import Participant



# Helpers (ортақ guard / redirect / queries)
# ----------------------------------------------------------------------------------------------------------------------
def hx_redirect(url: str) -> HttpResponse:
    resp = HttpResponse()
    resp['HX-Redirect'] = url
    return resp


def session_token_matches(request, participant: Participant) -> bool:
    return request.session.get('current_game_participant_token') == str(participant.token)


def cleanup_session_token_if_matches(request, participant: Participant) -> None:
    if request.session.get('current_game_participant_token') == str(participant.token):
        request.session.pop('current_game_participant_token', None)


def guard_session_state(participant: Participant, *, token, for_htmx: bool):
    session = participant.session
    if session.is_pending():
        url = reverse('main:gameplay_waiting', kwargs={'token': token})
        return None, (hx_redirect(url) if for_htmx else redirect('main:gameplay_waiting', token=token))
    if session.is_time_over() or session.is_finished() or participant.is_finished:
        url = reverse('main:gameplay_result', kwargs={'token': token})
        return None, (hx_redirect(url) if for_htmx else redirect('main:gameplay_result', token=token))

    return session, None


def get_participant_or_redirect(request, token, *, for_htmx: bool):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    if not session_token_matches(request, participant):
        url = reverse('main:gameplay_join')
        return None, (hx_redirect(url) if for_htmx else redirect('main:gameplay_join'))
    return participant, None


def load_questions(game_task):
    return list(
        game_task.questions.select_related('question').order_by('order', 'pk')
    )


def finish_participant(participant: Participant):
    if not participant.is_finished:
        participant.is_finished = True
        participant.finished_at = timezone.now()
        participant.save(update_fields=['is_finished', 'finished_at'])
