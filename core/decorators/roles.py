from functools import wraps
from django.http import Http404
from django.shortcuts import redirect


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if user.is_authenticated:
                if user.user_role == 'manager' and not request.path.startswith('/manage/'):
                    return redirect('manager_dashboard')

                if user.user_role == 'teacher' and not request.path.startswith('/teacher/'):
                    return redirect('teacher_dashboard')

                if user.user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)

            raise Http404('Page not found')

        return _wrapped_view
    return decorator
