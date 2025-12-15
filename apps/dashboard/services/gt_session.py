from django.shortcuts import get_object_or_404
from core.models import GameTaskSession, GameTask


def get_owned_session_or_404(user, pk, session_id):
    game_task = get_object_or_404(
        GameTask,
        pk=pk,
        owner=user,
        status='published',
    )
    session = get_object_or_404(
        GameTaskSession.objects.select_related('game_task'),
        pk=session_id,
        game_task=game_task,
    )
    return game_task, session