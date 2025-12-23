from django.urls import path
from .views import dashboard, account, game_task as gt, gt_session

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
    path('game-tasks/create/', gt.game_task_create_action, name='game_task_create'),
    path('game-tasks/<int:pk>/edit/', gt.game_task_edit_view, name='game_task_edit'),
    path('game-tasks/<int:pk>/edit/step/activity/', gt.game_task_step_activity, name='game_task_step_activity'),
    path('game-tasks/<int:pk>/edit/step/questions/', gt.game_task_step_questions, name='game_task_step_questions'),
    path('game-tasks/<int:pk>/edit/step/settings/', gt.game_task_step_settings, name='game_task_step_settings'),
    path('game-tasks/<int:pk>/publish/', gt.game_task_publish_view, name='game_task_publish'),
    path('game-tasks/<int:pk>/delete/', gt.game_task_delete_action, name='game_task_delete'),
    path('game-tasks/<int:pk>/', gt.game_task_detail_view, name='game_task_detail'),
    path('game-tasks/<int:pk>/questions/', gt.game_task_questions_view, name='game_task_questions'),

    # gt_session
    # ------------------------------------------------------------------------------------------------------------------
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/',
        gt_session.gt_session_route_action,
        name='session_route'
    ),
    path(
        'game-tasks/<int:pk>/sessions/create/',
        gt_session.gt_session_create_action,
        name='session_create'
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/waiting/',
        gt_session.gt_session_waiting_view,
        name='session_waiting'
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/participants/',
        gt_session.gt_session_participants_fragment,
        name='session_participants_fragment'
    ),
    path('game-tasks/<int:pk>/sessions/<int:session_id>/start/',
         gt_session.gt_session_start_action,
         name='session_start'
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/active/',
        gt_session.gt_session_active_view,
        name='session_active',
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/active/leaderboard/',
        gt_session.gt_session_active_leaderboard_fragment,
        name='session_active_leaderboard',
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/finished/',
        gt_session.gt_session_finished_view,
        name='session_finished',
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/delete/',
        gt_session.gt_session_delete_action,
        name='session_delete'
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/finish/',
        gt_session.gt_session_finish_action,
        name='session_finish',
    ),
    path(
        'game-tasks/<int:pk>/sessions/<int:session_id>/settings/',
        gt_session.gt_session_settings_action,
        name='session_settings',
    ),
]
