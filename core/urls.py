from django.urls import path
from .views import get_variants


urlpatterns = [
    path('get_variants/', get_variants, name='get_variants'),
]
