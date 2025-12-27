from __future__ import annotations
import random
from django.db.models import Case, When, IntegerField
from dataclasses import dataclass
from django.template.loader import select_template


# Scoring жүйесі
# ----------------------------------------------------------------------------------------------------------------------
@dataclass
class ScoreResult:
    score: int
    is_correct: bool
    time_spent: int


BASE_MAX_SCORE = 1000
BASE_MIN_SCORE = 500


def calculate_question_score(*, question, is_correct: bool, time_spent: int) -> ScoreResult:
    if not is_correct:
        return ScoreResult(score=0, is_correct=False, time_spent=time_spent)

    t_limit = getattr(question, 'question_limit', None) or 0
    if t_limit <= 0:
        return ScoreResult(score=BASE_MIN_SCORE, is_correct=True, time_spent=time_spent)

    if time_spent < 0:
        time_spent = 0

    speed = (t_limit - time_spent) / float(t_limit)
    if speed < 0:
        speed = 0.0
    elif speed > 1:
        speed = 1.0

    # 5) Финалдық ұпай
    score_float = BASE_MIN_SCORE + (BASE_MAX_SCORE - BASE_MIN_SCORE) * speed
    score_int = int(round(score_float))

    return ScoreResult(score=score_int, is_correct=True, time_spent=time_spent)



# Activity шаблон жүйесі
# ----------------------------------------------------------------------------------------------------------------------
def resolve_activity_template(activity, name: str) -> str:
    fallback_group = 'games'
    fallback_slug = 'quiz'
    if activity and activity.activity_type == 'simulator':
        group = 'simulators'
    else:
        group = 'games'

    slug = activity.slug if activity else fallback_slug
    candidates = [
        f"activity/{group}/{slug}/{name}",
        f"activity/{fallback_group}/{fallback_slug}/{name}",
    ]
    return select_template(candidates).template.name


# Fixed options
# ----------------------------------------------------------------------------------------------------------------------
def _opt_order_key(participant, question_id: int) -> str:
    return f"opt_order:{participant.token}:{question_id}"


def get_or_create_options_in_fixed_order(request, participant, question):
    key = _opt_order_key(participant, question.id)
    order = request.session.get(key)
    ids = list(question.options.values_list('id', flat=True))
    if not ids:
        return question.options.none(), []

    if not order:
        order = ids[:]
        random.shuffle(order)
        request.session[key] = order
        request.session.modified = True
    else:
        ids_set = set(ids)
        order = [i for i in order if i in ids_set]
        for i in ids:
            if i not in set(order):
                order.append(i)
        request.session[key] = order
        request.session.modified = True

    whens = [When(id=pk, then=pos) for pos, pk in enumerate(order)]
    qs = question.options.filter(id__in=order).order_by(
        Case(*whens, default=9999, output_field=IntegerField())
    )
    return qs, order
