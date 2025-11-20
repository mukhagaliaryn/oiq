from django.urls import path
from .views import main, account


urlpatterns = [
    # main views...
    path('', main.teacher_dashboard_view, name='teacher_dashboard'),
    path('classes/', main.teacher_classes_view, name='teacher_classes'),
    path('classes/<pk>/', main.teacher_class_view, name='teacher_class'),
    path('pupils/', main.teacher_pupils_view, name='teacher_pupils'),

    # account views...
    path('settings/account/', account.teacher_account_view, name='teacher_account'),
    path('settings/security/', account.teacher_security_view, name='teacher_security'),
]
