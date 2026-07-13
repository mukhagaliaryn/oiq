from functools import wraps
from django.core.exceptions import PermissionDenied


def org_role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.membership or not request.membership.has_role(*roles):
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
