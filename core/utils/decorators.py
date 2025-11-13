from functools import wraps
from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect


def role_required(*allowed_roles, raise_404=True):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            if getattr(user, 'user_role', None) in allowed_roles:
                return view_func(request, *args, **kwargs)

            if raise_404:
                raise Http404("Page not found")
            raise Http404("Page not found")
        return _wrapped_view
    return decorator
