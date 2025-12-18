from __future__ import annotations
from dataclasses import dataclass
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from core.models import Participant


# Scoring жүйесі
# ----------------------------------------------------------------------------------------------------------------------
@dataclass
class ScoreResult:
    score: int
    is_correct: bool
    time_spent: int


BASE_MAX_SCORE = 1000
BASE_MIN_SCORE = 500


def calculate_question_score(
    *,
    question,
    is_correct: bool,
    time_spent: int,
) -> ScoreResult:
    """
    Kahoot-қа ұқсас скоринг.

    Идея:
    - Қате болса → 0
    - Дұрыс болса → 500–1000 аралығында, question.question_limit және time_spent-ке байланысты.

    Параметрлер:
    - question.question_limit – бұл сұраққа "нормальный" ойлауға берілетін уақыт (секунд).
      Егер сен minutes-пен сақтасаң, онда алдын-ала 60-қа көбейтіп жіберу керек.
    - time_spent – нақты жұмсаған уақыт (секунд).

    Формула (қысқаша):
        t_limit = question_limit
        t = time_spent

        speed = (t_limit - t) / t_limit   (0..1 арасы)
        score = MIN + (MAX - MIN) * speed

        t <= 0     → speed ~ 1   → ≈ 1000
        t >= t_lim → speed = 0   → 500
    """

    # 1) Қате болса – бірден 0
    if not is_correct:
        return ScoreResult(score=0, is_correct=False, time_spent=time_spent)

    # 2) question_limit-ті аламыз
    # МОДЕЛЬДЕ: question_limit = PositiveSmallIntegerField(default=30)
    # Біз оны СЕКУНД деп қабылдаймыз.
    # Егер реально minutes сақтағың келсе, answer view-да алдын ала * 60 жасайсың.
    t_limit = getattr(question, 'question_limit', None) or 0

    # Егер лимит 0 немесе теріс болса – speed бонус қолданбаймыз, тек мин. бонус
    if t_limit <= 0:
        return ScoreResult(
            score=BASE_MIN_SCORE,
            is_correct=True,
            time_spent=time_spent,
        )

    # 3) Time_spent-ті clamp жасаймыз (теріс болса 0 қыламыз)
    if time_spent < 0:
        time_spent = 0

    # 4) Speed ratio (0..1) есептеу
    # time_spent <= 0  → speed = 1.0 (ең жылдам)
    # time_spent >= t_limit → speed = 0.0 (лимитке дейін немесе асып кеткен)
    speed = (t_limit - time_spent) / float(t_limit)
    if speed < 0:
        speed = 0.0
    elif speed > 1:
        speed = 1.0

    # 5) Финалдық ұпай
    score_float = BASE_MIN_SCORE + (BASE_MAX_SCORE - BASE_MIN_SCORE) * speed
    score_int = int(round(score_float))

    return ScoreResult(
        score=score_int,
        is_correct=True,
        time_spent=time_spent,
    )


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


def get_participant_or_redirect(request, token, *, for_htmx: bool):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    if not session_token_matches(request, participant):
        url = reverse('main:gameplay_join')
        return None, (hx_redirect(url) if for_htmx else redirect('main:gameplay_join'))
    return participant, None


def guard_session_state(participant: Participant, *, token, for_htmx: bool):
    session = participant.session
    if session.is_pending():
        url = reverse('main:gameplay_waiting', kwargs={'token': token})
        return None, (hx_redirect(url) if for_htmx else redirect('main:gameplay_waiting', token=token))
    if session.is_time_over() or session.is_finished() or participant.is_finished:
        url = reverse('main:gameplay_result', kwargs={'token': token})
        return None, (hx_redirect(url) if for_htmx else redirect('main:gameplay_result', token=token))

    return session, None


def load_questions(game_task):
    return list(
        game_task.questions.select_related('question').order_by('order', 'pk')
    )


def finish_participant(participant: Participant):
    if not participant.is_finished:
        participant.is_finished = True
        participant.finished_at = timezone.now()
        participant.save(update_fields=['is_finished', 'finished_at'])
