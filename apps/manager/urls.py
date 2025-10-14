from django.urls import path
from .views import main


urlpatterns = [
    path('', main.manager_dashboard_view, name='manager_dashboard'),
]
