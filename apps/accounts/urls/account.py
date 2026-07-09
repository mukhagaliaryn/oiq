from django.urls import path
from apps.accounts.views import account

urlpatterns = [
    path('profile/<str:username>/', account.profile_view, name='profile'),
    path('edit/', account.account_edit_view, name='account-edit'),
    path('settings/', account.account_settings_view, name='account-settings'),
    path('security/', account.account_security_view, name='account-security'),
]
