from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('upload/', views.ckeditor_image_upload, name='ckeditor-upload'),
]
