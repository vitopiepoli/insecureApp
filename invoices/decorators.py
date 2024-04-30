from django.http import HttpResponse
from functools import wraps

def user_role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponse("Please log in to view this page.", status=401)
            if any(group.name in allowed_roles for group in request.user.groups.all()):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("Unauthorized access", status=403)
        return _wrapped_view
    return decorator