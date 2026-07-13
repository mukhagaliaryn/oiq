from django.urls import path
from .views import account, main, question, question_import, subject


app_name = 'teaching'


urlpatterns = [
    path('', main.dashboard_view, name='dashboard'),

    path('account/profile/<str:username>/', account.profile_view, name='profile'),
    path('account/edit/', account.account_edit_view, name='account-edit'),
    path('account/settings/', account.account_settings_view, name='account-settings'),
    path('account/security/', account.account_security_view, name='account-security'),

    path('subject/<int:pk>/', subject.subject_detail_view, name='subject-detail'),
    path('subject/<int:pk>/update/', subject.subject_update_view, name='subject-update'),
    path('subject/<int:pk>/remove-cover/', subject.subject_remove_cover_view, name='subject-remove-cover'),
    path('subject/<int:pk>/chapters/create/', subject.chapter_create_view, name='chapter-create'),
    path('chapters/<int:pk>/update/', subject.chapter_update_view, name='chapter-update'),
    path('chapters/<int:pk>/delete/', subject.chapter_delete_view, name='chapter-delete'),
    path('chapters/<int:pk>/topics/create/', subject.topic_create_view, name='topic-create'),
    path('topics/<int:pk>/update/', subject.topic_update_view, name='topic-update'),
    path('topics/<int:pk>/delete/', subject.topic_delete_view, name='topic-delete'),

    path('subject/<int:pk>/questions/', question.question_list_view, name='question-list'),
    path('subject/<int:pk>/questions/create/', question.question_create_view, name='question-create'),
    path('questions/<int:pk>/update/', question.question_update_view, name='question-update'),
    path('questions/<int:pk>/delete/', question.question_delete_view, name='question-delete'),
    path('questions/variant-field/', question.question_variant_field_view, name='question-variant-field'),
    path('questions/topic-fields/', question.question_topic_fields_view, name='question-topic-fields'),

    path('subject/<int:pk>/questions/import/', question_import.question_import_view, name='question-import'),
    path(
        'subject/<int:pk>/questions/import/<str:import_id>/',
        question_import.question_import_review_view, name='question-import-review',
    ),
    path(
        'subject/<int:pk>/questions/import/<str:import_id>/cancel/',
        question_import.question_import_cancel_view, name='question-import-cancel',
    ),
    path(
        'subject/<int:pk>/questions/import/<str:import_id>/confirm/',
        question_import.question_import_confirm_view, name='question-import-confirm',
    ),
]
