from core.models import GameTaskSession
import re


# views
# ----------------------------------------------------------------------------------------------------------------------
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


def get_unique_nickname_for_session(session, base_nickname: str) -> str:
    base = base_nickname.strip()
    existing = session.participants.filter(nickname=base).exists()
    if not existing:
        return base

    similar_qs = session.participants.filter(nickname__startswith=base)
    max_suffix = 1
    pattern = re.compile(rf'^{re.escape(base)}(?: \((\d+)\))?$')
    for p in similar_qs:
        m = pattern.match(p.nickname)
        if not m:
            continue
        if m.group(1):
            num = int(m.group(1))
            if num >= max_suffix:
                max_suffix = num + 1
        else:
            if max_suffix <= 1:
                max_suffix = 2

    if max_suffix == 1:
        return base
    return f"{base} ({max_suffix})"


# actions
# ----------------------------------------------------------------------------------------------------------------------
# ...