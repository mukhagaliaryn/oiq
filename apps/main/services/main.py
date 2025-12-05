from core.models import GameTaskSession


def get_joinable_session_by_pin(pin_code: str):
    if not pin_code:
        return None
    session = (
        GameTaskSession.objects
        .select_related('game_task')
        .filter(pin_code=pin_code)
        .first()
    )
    if not session:
        return None

    if not session.is_joinable():
        return None

    return session