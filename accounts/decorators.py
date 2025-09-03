from functools import wraps
from django.contrib.auth.decorators import user_passes_test


def role_required(role):
    """Return a decorator that allows access only to users with the given role.

    Accepts 'student', 'professor', or 'admin'. Admins (staff) pass automatically.
    Usage:
        @role_required('professor')
        def my_view(request):
            ...
    """
    def check(user):
        try:
            if role == 'admin':
                return user.is_staff
            return user.userprofile.role == role or user.is_staff
        except Exception:
            return user.is_staff if role == 'admin' else False

    return user_passes_test(check)


def allow_roles(*roles):
    """Decorator that allows access to any of the provided roles or staff users.

    Example: @allow_roles('student', 'professor')
    """
    def decorator(view_func):
        def check(user):
            try:
                if user.is_staff:
                    return True
                return getattr(user, 'userprofile', None) and user.userprofile.role in roles
            except Exception:
                return user.is_staff

        return user_passes_test(check)(view_func)

    return decorator
