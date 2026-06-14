from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('ckeditor/upload/', views.ckeditor_image_upload, name='ckeditor-upload'),
    path('format-variants/', views.format_variants, name='format-variants'),
]
