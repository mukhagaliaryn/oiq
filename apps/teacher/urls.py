from django.urls import path
from .views import main, account


urlpatterns = [
    path('', main.teacher_dashboard_view, name='teacher_dashboard'),

    # account views...
    path('account/profile/', account.teacher_profile_view, name='teacher_profile'),
]