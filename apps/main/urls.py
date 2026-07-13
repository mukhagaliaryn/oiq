from django.urls import path
from .views import auth, main

app_name = 'main'

urlpatterns = [
    path('', main.main_view, name='main'),

    path('auth/login/', auth.login_view, name='login'),
    path('auth/logout/', auth.logout_view, name='logout'),
    path('auth/register/', auth.register_select_view, name='register'),
    path('auth/register/learner/', auth.learner_register_view, name='learner-register'),
    path('auth/register/teacher/', auth.teacher_register_view, name='teacher-register'),
]
