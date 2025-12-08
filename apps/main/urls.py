from django.urls import path
from .views import main, auth, gameplay

app_name = 'main'

urlpatterns= [
    # main views...
    path('', main.main_view, name='main'),
    path('join/', gameplay.gameplay_join_view, name='gameplay_join'),
    path('wait/<uuid:token>/', gameplay.gameplay_waiting_view, name='gameplay_waiting'),
    path('wait/<uuid:token>/poll/', gameplay.gameplay_waiting_poll_fragment, name='gameplay_waiting_poll'),
    path('play/<uuid:token>/', main.gt_session_play_view, name='session_play'),
    path('play/<uuid:token>/answer', main.gt_session_answer_view, name='session_answer'),
    path('play/<uuid:token>/finish/', main.gt_session_finish_participant_action, name='session_finish_participant'),
    path('play/<uuid:token>/result/', main.gt_session_result_view, name='session_result'),

    # auth views...
    path('login/', auth.login_view, name='login'),
    path('register/', auth.register_view, name='register'),
    path('logout/', auth.logout_view, name='logout'),
]
