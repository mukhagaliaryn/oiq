from core.models import GameTask


# get_game_task_current_step
def get_game_task_current_step(game_task: GameTask) -> str:
    if game_task.activity_id is None:
        return 'activity'
    if not game_task.questions.exists():
        return 'questions'
    if not game_task.name:
        return 'settings'
    return 'settings'
