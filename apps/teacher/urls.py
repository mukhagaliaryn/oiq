from django.urls import path
from .views import account, dashboard, game_task, game_task_session

app_name = 'teacher'

urlpatterns = [
    # dashboard
    # ------------------------------------------------------------------------------------------------------------------
    path('', dashboard.dashboard_view, name='dashboard'),
    path('game-tasks/', dashboard.game_tasks_view, name='game_tasks'),
    path('game-tasks/drafts/', dashboard.game_task_drafts_view, name='game_task_drafts'),
    path('game-tasks/archives/', dashboard.game_task_archives_view, name='game_task_archives'),

    # account
    # ------------------------------------------------------------------------------------------------------------------
    path('settings/account/', account.account_view, name='account'),
    path('settings/security/', account.security_view, name='security'),

    # game_task
    # ------------------------------------------------------------------------------------------------------------------
    path('game-tasks/create/', game_task.game_task_create_view, name='game_task_create'),
    path('game-tasks/<int:pk>/edit/', game_task.game_task_edit_view, name='game_task_edit'),
    path('game-tasks/<int:pk>/edit/step/activity/', game_task.game_task_step_activity, name='game_task_step_activity'),
    path('game-tasks/<int:pk>/edit/step/questions/', game_task.game_task_step_questions, name='game_task_step_questions'),
    path('game-tasks/<int:pk>/edit/step/settings/', game_task.game_task_step_settings, name='game_task_step_settings'),
    path('game-tasks/<int:pk>/publish/', game_task.game_task_publish_view, name='game_task_publish'),

    path('game-tasks/<int:pk>/', game_task.game_task_detail_view, name='game_task_detail'),
    path('game-tasks/<int:pk>/questions/', game_task.game_task_questions_view, name='game_task_questions'),

    # game_task_session
    # ------------------------------------------------------------------------------------------------------------------
    path('game-task/live/session/<int:pk>/', game_task_session.game_task_session_view, name='game_task_live_session'),
]
