from django.urls import path
from .views import main, auth

app_name = 'main'

urlpatterns= [
    # main views...
    path('', main.main_view, name='main'),
    path('join/', main.gt_session_join_view, name='session_join'),
    path('wait/<uuid:token>/', main.gt_session_waiting_view, name='session_waiting'),
    path('wait/<uuid:token>/poll/', main.gt_session_waiting_poll_view, name='session_waiting_poll'),
    path('play/<uuid:token>/', main.gt_session_play_view, name='session_play'),
    path('play/<uuid:token>/finish/', main.gt_session_finish_participant_action, name='session_finish_participant'),
    path('play/<uuid:token>/result/', main.gt_session_result_view, name='session_result'),

    # auth views...
    path('login/', auth.login_view, name='login'),
    path('register/', auth.register_view, name='register'),
    path('logout/', auth.logout_view, name='logout'),
]
