from django.urls import path
from .views import main, account


urlpatterns = [
    path('', main.teacher_dashboard_view, name='teacher_dashboard'),

    # account views...
    path('settings/account/', account.teacher_account_view, name='teacher_account'),
    path('settings/security/', account.teacher_security_view, name='teacher_security'),
]
