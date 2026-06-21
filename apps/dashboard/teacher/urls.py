from django.urls import path
from .views import account, main


app_name = 'teacher'


urlpatterns = [
    path('', main.dashboard_view, name='dashboard'),

    path('profile/<str:username>/', account.profile_view, name='profile'),
    path('account/edit/', account.account_edit_view, name='account-edit'),
    path('account/settings/', account.account_settings_view, name='account-settings'),
    path('account/security/', account.account_security_view, name='account-security'),
]
