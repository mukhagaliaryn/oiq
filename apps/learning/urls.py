from django.urls import path
from .views import account, main

app_name = 'learning'

urlpatterns = [
    path('', main.dashboard_view, name='dashboard'),
    path('account/', account.account_view, name='account'),
]
