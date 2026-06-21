from django.urls import path
from .views import account, main, subject


app_name = 'teacher'


urlpatterns = [
    path('', main.dashboard_view, name='dashboard'),

    path('profile/<str:username>/', account.profile_view, name='profile'),
    path('account/edit/', account.account_edit_view, name='account-edit'),
    path('account/settings/', account.account_settings_view, name='account-settings'),
    path('account/security/', account.account_security_view, name='account-security'),

    path('subject/<int:pk>/', subject.subject_detail_view, name='subject-detail'),
    path('subject/<int:pk>/chapters/create/', subject.chapter_create_view, name='chapter-create'),
    path('chapters/<int:pk>/update/', subject.chapter_update_view, name='chapter-update'),
    path('chapters/<int:pk>/delete/', subject.chapter_delete_view, name='chapter-delete'),
    path('chapters/<int:pk>/topics/create/', subject.topic_create_view, name='topic-create'),
    path('topics/<int:pk>/update/', subject.topic_update_view, name='topic-update'),
    path('topics/<int:pk>/delete/', subject.topic_delete_view, name='topic-delete'),
]
