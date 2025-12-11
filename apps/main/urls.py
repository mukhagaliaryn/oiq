from django.urls import path
from .views import main, auth, gameplay

app_name = 'main'

urlpatterns= [
    # main views...
    path('', main.main_view, name='main'),
    path('join/', gameplay.gameplay_join_view, name='gameplay_join'),
    path('wait/<uuid:token>/', gameplay.gameplay_waiting_view, name='gameplay_waiting'),
    path('wait/<uuid:token>/poll/', gameplay.gameplay_waiting_poll_fragment, name='gameplay_waiting_poll'),
    path('play/<uuid:token>/', gameplay.gameplay_play_view, name='gameplay_play'),
    path('play/<uuid:token>/answer', gameplay.gameplay_answer_action, name='gameplay_answer'),
    path('play/<uuid:token>/question/', gameplay.gameplay_question_fragment, name='gameplay_question'),
    path('play/<uuid:token>/finish/', gameplay.gameplay_finish_action, name='gameplay_finish'),
    path('play/<uuid:token>/result/', gameplay.gameplay_result_view, name='gameplay_result'),

    # auth views...
    path('login/', auth.login_view, name='login'),
    path('register/', auth.register_view, name='register'),
    path('logout/', auth.logout_view, name='logout'),
]
