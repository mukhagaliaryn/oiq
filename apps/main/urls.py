from django.urls import path
from .views import main

app_name = 'main'

urlpatterns = [
    path('', main.main_view, name='main'),
]
