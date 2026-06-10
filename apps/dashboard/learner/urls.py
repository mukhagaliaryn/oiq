from django.urls import path
from .views import main


app_name = 'learner'


urlpatterns = [
    path('', main.dashboard_view, name='dashboard'),
]
