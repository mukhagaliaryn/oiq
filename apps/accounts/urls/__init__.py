from django.urls import include, path
from . import auth, account

app_name = 'accounts'

urlpatterns = [
    path('auth/', include(auth)),
    path('account/', include(account)),
]
