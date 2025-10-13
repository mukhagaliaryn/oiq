from django.urls import path
from .views import main


urlpatterns = [
    path('', main.learner_home_view, name='learner_home'),
    path('games/', main.learner_games_view, name='learner_games')
]