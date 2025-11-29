from functools import wraps
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import Http404


def role_required(*allowed_roles, raise_404=True):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

            if getattr(user, 'user_role', None) in allowed_roles:
                return view_func(request, *args, **kwargs)

            if raise_404:
                raise Http404('Page not found')
            raise Http404('Page not found')
        return _wrapped_view
    return decorator
