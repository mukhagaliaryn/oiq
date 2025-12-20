from __future__ import annotations
from dataclasses import dataclass


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

