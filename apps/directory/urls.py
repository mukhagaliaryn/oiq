from django.urls import path
from apps.directory import views

app_name = 'directory'

urlpatterns = [
    path('school-field/', views.school_field_view, name='school-field'),
]
