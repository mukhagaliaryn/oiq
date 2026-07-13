from django.urls import path
from apps.school.views import landing

urlpatterns = [
    path('', landing.landing_view, name='landing'),
]
