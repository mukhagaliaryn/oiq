from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ScoreResult:
    score: int
    is_correct: bool
    time_spent: int


BASE_MAX_SCORE = 1000  # өте жылдам және дұрыс жауап
BASE_MIN_SCORE = 500   # өте баяу болса да, дұрыс жауап үшін минималды бонус


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
    t_limit = getattr(question, "question_limit", None) or 0

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
