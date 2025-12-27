from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AnswerResult:
    answered: bool
    is_correct: Optional[bool]
    score_delta: int
    payload: Dict[str, Any]


class BaseHandler:
    code: str = 'base'

    def get_question_context(self, *, request, participant, question, gtq) -> Dict[str, Any]:
        return {}

    def parse_and_grade(self, *, request, participant, question, gtq, is_timeout: bool, time_spent: int) -> AnswerResult:
        raise NotImplementedError

    def save_answer(self, *, participant, question, gtq, attempt, payload: Dict[str, Any]) -> None:
        return

    def get_review_context(self, *, request, participant, question, gtq, payload: Dict[str, Any]) -> Dict[str, Any]:
        return payload
