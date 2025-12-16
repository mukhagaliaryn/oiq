# game_task_step_questions
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional
from django.db import transaction
from core.models import GameTaskQuestion, Question


@dataclass(frozen=True)
class QuestionPickResult:
    picked: list[Question]
    warning: Optional[str] = None


def _pick_random(qs, limit: int) -> list[Question]:
    return list(qs.order_by('?')[:limit])


def generate_questions_for_game_task(
    *,
    game_task,
    qs,
    total_count: int,
    selected_levels: Optional[list[str]] = None,
) -> QuestionPickResult:
    if total_count <= 0:
        return QuestionPickResult([], 'Сұрақ санын дұрыс енгізіңіз.')

    if not selected_levels:
        available = qs.count()
        if available == 0:
            return QuestionPickResult([], 'Берілген фильтр бойынша сұрақ табылмады.')

        take = min(total_count, available)
        picked = _pick_random(qs, take)

        warning = None
        if take < total_count:
            warning = (
                f"Берілген фильтр бойынша тек {take} сұрақ табылды. "
                f"Қалғаны базада жоқ."
            )
        return QuestionPickResult(picked, warning)

    level_codes = selected_levels
    base_part = total_count // len(level_codes)
    remainder = total_count % len(level_codes)

    level_to_target = {
        code: base_part + (1 if idx < remainder else 0)
        for idx, code in enumerate(level_codes)
    }

    picked_ids: set[int] = set()
    picked: list[Question] = []

    for level_code in level_codes:
        need = level_to_target.get(level_code, 0)
        if need <= 0:
            continue

        chunk = _pick_random(
            qs.filter(level=level_code).exclude(id__in=picked_ids),
            need,
        )
        for q in chunk:
            picked_ids.add(q.pk)
            picked.append(q)

    missing = total_count - len(picked)
    if missing > 0:
        filler = _pick_random(qs.filter(level__in=level_codes).exclude(id__in=picked_ids), missing)
        picked.extend(filler)

    if not picked:
        return QuestionPickResult([], 'Берілген фильтр бойынша сұрақ табылмады.')

    warning = None
    if len(picked) < total_count:
        warning = (
            f"Берілген фильтр бойынша тек {len(picked)} сұрақ табылды. "
            f"Қалғаны базада жоқ."
        )
    return QuestionPickResult(picked, warning)


@transaction.atomic
def replace_game_task_questions(
    *,
    game_task,
    questions: Iterable[Question],
) -> None:
    GameTaskQuestion.objects.filter(game_task=game_task).delete()
    rows = [
        GameTaskQuestion(game_task=game_task, question=q, order=i)
        for i, q in enumerate(questions, start=1)
    ]
    if rows:
        GameTaskQuestion.objects.bulk_create(rows)
