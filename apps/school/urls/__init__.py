from django.urls import include, path
from apps.school.views import auth
from . import landing, workspace

app_name = 'school'

urlpatterns = [
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),

    path('', include(landing)),
    path('<slug:org>/', include(workspace)),
]
