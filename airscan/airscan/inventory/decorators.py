from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    RBAC decorator - OWASP ASVS V4 / A5
    Enforces access control on all endpoints
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Check if user has required role
            if 'admin' in allowed_roles and request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            elif 'user' in allowed_roles and not request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            elif not allowed_roles:  # Any authenticated user
                return view_func(request, *args, **kwargs)
            else:
                # Raise PermissionDenied to trigger 403 error
                raise PermissionDenied("You don't have permission to access this resource.")
        return wrapper
    return decorator


def prevent_idor(queryset_func):
    """
    Prevent Insecure Direct Object Reference (IDOR)
    Ensures user can only access their own objects (or admin can access all)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            obj_id = kwargs.get('pk')
            if obj_id:
                # Get the object using the provided queryset function
                try:
                    queryset = queryset_func(request)
                    obj = queryset.get(pk=obj_id)
                    # Add object to kwargs for the view
                    kwargs['object'] = obj
                except Exception:
                    messages.error(request, 'Item not found or access denied.')
                    return redirect('inventory_list')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator