from django.urls import path
from apps.catalog import views

app_name = 'catalog'

urlpatterns = [
    path('format-variants/', views.format_variants, name='format-variants'),
]
