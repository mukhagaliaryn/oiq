from django.urls import path
from .views import dashboard, account, game_task, gt_session as gt

app_name = 'dashboard'

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
    path('game-tasks/<int:pk>/delete/', game_task.game_task_delete_action, name='game_task_delete'),

    path('game-tasks/<int:pk>/', game_task.game_task_detail_view, name='game_task_detail'),
    path('game-tasks/<int:pk>/questions/', game_task.game_task_questions_view, name='game_task_questions'),

    # gt_session
    # ------------------------------------------------------------------------------------------------------------------
    # pages...
    path('game-tasks/<int:pk>/sessions/<int:session_id>/', gt.gt_session_view, name='session'),
    path('game-tasks/<int:pk>/sessions/create/', gt.gt_session_create_view, name='session_create'),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/waiting/',
        gt.game_task_session_waiting_view,
        name='session_waiting'
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/participants/',
        gt.gt_session_participants_fragment,
        name='session_participants_fragment'
    ),
    path('game-tasks/<int:pk>/sessions/<int:session_id>/start/',
         gt.gt_session_start_action,
         name='session_start'
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/active/',
        gt.gt_session_active_view,
        name='session_active',
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/active/leaderboard/',
        gt.gt_session_active_leaderboard_fragment,
        name='session_active_leaderboard',
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/finished/',
        gt.gt_session_finished_view,
        name='session_finished',
    ),

    # actions...
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/delete/',
        gt.gt_session_delete_action,
        name='session_delete'
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/finish/',
        gt.gt_session_finish_action,
        name='session_finish',
    ),
]
