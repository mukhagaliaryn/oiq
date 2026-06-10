from django.urls import path
from .views import main, auth

app_name = 'main'

urlpatterns= [
    path('', main.main_view, name='main'),

    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    path('register/', auth.register_select_view, name='register'),
    path('register/learner/', auth.learner_register_view, name='learner-register'),
    path('register/teacher/', auth.teacher_register_view, name='teacher-register'),
    path('api/schools/', auth.schools_by_city_view, name='schools-by-city'),
]
