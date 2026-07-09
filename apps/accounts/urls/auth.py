from django.urls import path
from apps.accounts.views import auth

urlpatterns = [
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    path('register/', auth.register_select_view, name='register'),
    path('register/learner/', auth.learner_register_view, name='learner-register'),
    path('register/teacher/', auth.teacher_register_view, name='teacher-register'),
]
