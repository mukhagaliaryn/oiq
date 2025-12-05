from django.urls import path
from .views import main, auth

app_name = 'main'

urlpatterns= [
    # main views...
    path('', main.main_view, name='main'),
    path('join/', main.game_task_session_join_view, name='session_join'),
    path('play/<uuid:token>/', main.game_task_session_play_view, name='session_play'),

    # auth views...
    path('login/', auth.login_view, name='login'),
    path('register/', auth.register_view, name='register'),
    path('logout/', auth.logout_view, name='logout'),
]
