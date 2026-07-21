from django.urls import path
from apps.catalog import views

app_name = 'catalog'

urlpatterns = [
    path('format-variants/', views.format_variants, name='format-variants'),
    path('school-field/', views.school_field_view, name='school-field'),
]
