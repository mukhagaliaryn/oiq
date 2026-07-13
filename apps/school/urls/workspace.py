from django.urls import path
from apps.school.views import account, workspace, members

urlpatterns = [
    path('', workspace.dashboard_view, name='dashboard'),
    path('account/', account.account_view, name='account'),

    path('members/', members.member_list_view, name='member-list'),
    path('members/search/', members.member_search_view, name='member-search'),
    path('members/add/', members.member_add_view, name='member-add'),
    path('members/register/', members.member_register_view, name='member-register'),
    path('members/<int:membership_id>/roles/', members.member_update_roles_view, name='member-update-roles'),
    path('members/<int:membership_id>/remove/', members.member_remove_view, name='member-remove'),
]
