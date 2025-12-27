from __future__ import annotations
from typing import Dict
from .base import BaseHandler


_HANDLERS: Dict[str, BaseHandler] = {}

def register(handler_cls):
    _HANDLERS[handler_cls.code] = handler_cls()
    return handler_cls

def get_handler_for_question(question) -> BaseHandler:
    code = getattr(getattr(question, 'format', None), 'code', None) or 'test'
    return _HANDLERS.get(code) or _HANDLERS['test']
