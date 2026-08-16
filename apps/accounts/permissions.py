from functools import wraps

from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        if request.user.role != request.user.Role.ADMIN:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapped_view