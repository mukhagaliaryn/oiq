from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from apps.main.services.auth import get_user_redirect_url


def anonymous_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_user_redirect_url(request.user))

        return view_func(request, *args, **kwargs)

    return wrapper


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def learner_required(view_func):
    return role_required('learner')(view_func)


def teacher_required(view_func):
    return role_required('teacher')(view_func)


def admin_required(view_func):
    return role_required('admin')(view_func)


def partner_teacher_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        is_partner = (
            request.user.role == request.user.Role.TEACHER
            and hasattr(request.user, 'teacher')
            and request.user.teacher.is_partner
        )

        if not is_partner:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper