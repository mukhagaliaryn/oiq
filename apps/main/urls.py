from django.urls import path
from .views import main, auth

urlpatterns= [
    # main views...
    path('', main.main_view, name='main'),

    # auth views...
    path('login/', auth.login_view, name='login'),
    path('register/', auth.register_view, name='register'),
    path('logout/', auth.logout_view, name='logout'),
]
