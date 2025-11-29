from django.urls import path
from .views import main


urlpatterns = [
    path('', main.learner_dashboard_view, name='learner_dashboard'),
    path('games/', main.learner_games_view, name='learner_games')
]