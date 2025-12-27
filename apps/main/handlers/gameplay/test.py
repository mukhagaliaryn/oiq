from __future__ import annotations
from typing import Dict, Any, Set
from core.models import TestAnswer, Option
from .base import BaseHandler, AnswerResult
from .registry import register
from ...services.gameplay_play import get_or_create_options_in_fixed_order, calculate_question_score


@register
class TestHandler(BaseHandler):
    code = 'test'

    def get_question_context(self, *, request, participant, question, gtq) -> Dict[str, Any]:
        options_qs, _ = get_or_create_options_in_fixed_order(request, participant, question)
        return {'options': list(options_qs)}

    def parse_and_grade(
        self, *, request, participant, question, gtq, is_timeout: bool, time_spent: int,
    ) -> AnswerResult:
        selected_ids = [int(pk) for pk in request.POST.getlist('options') if pk.isdigit()]

        if is_timeout:
            selected_ids = []

        allowed_ids: Set[int] = set(question.options.values_list('id', flat=True))
        selected_ids = [i for i in selected_ids if i in allowed_ids]
        selected_set = set(selected_ids)
        correct_ids: Set[int] = set(question.options.filter(is_correct=True).values_list('id', flat=True))
        answered = bool(selected_ids) and not is_timeout

        if not answered:
            return AnswerResult(
                answered=False,
                is_correct=None,
                score_delta=0,
                payload={'selected_ids': selected_ids, 'correct_ids': list(correct_ids)},
            )

        if not correct_ids:
            is_correct = False
        else:
            q_type = question.variant.code if getattr(question, 'variant', None) else 'single'
            if q_type == 'multiple':
                is_correct = (selected_set == correct_ids)
            else:
                one = next(iter(selected_set), None)
                is_correct = (len(selected_set) == 1 and one in correct_ids)

        score = calculate_question_score(question=question, is_correct=is_correct, time_spent=time_spent).score
        score_delta = score if is_correct else 0

        return AnswerResult(
            answered=True,
            is_correct=is_correct,
            score_delta=score_delta,
            payload={'selected_ids': selected_ids, 'correct_ids': list(correct_ids)},
        )

    def save_answer(self, *, participant, question, gtq, attempt, payload: Dict[str, Any]) -> None:
        test_answer = TestAnswer.objects.create(attempt=attempt)
        selected_ids = payload.get('selected_ids') or []
        if selected_ids:
            test_answer.selected_options.set(Option.objects.filter(id__in=selected_ids))

    def get_review_context(self, *, request, participant, question, gtq, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'selected_ids': payload.get('selected_ids', []),
            'correct_ids': payload.get('correct_ids', []),
        }
