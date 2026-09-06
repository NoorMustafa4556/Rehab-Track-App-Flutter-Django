from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def admin_required(function=None, redirect_field_name=None, login_url='/admin-panel/login/'):
    """
    Decorator for views that checks that the user is logged in and is an Admin,
    raising PermissionDenied if not, or redirecting to login page.
    """
    def check_is_admin(user):
        if not user.is_authenticated:
            return False
        # Safe fallback: has_permission checks the cache and falls back to role_name if empty
        if user.has_permission('can_access_admin_panel') or (user.role_id and user.role_id.role_name == 'Admin'):
            return True
        raise PermissionDenied("You do not have permission to access the Admin Panel.")
        
    actual_decorator = user_passes_test(
        check_is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def portal_required(function=None, redirect_field_name=None, login_url='/portal/login/'):
    """
    Decorator for Client Portal views. Checks that user is logged in
    and is NOT an Admin (i.e. is a Patient or Clinician).
    """
    def check_is_portal_user(user):
        if not user.is_authenticated:
            return False
        # If user is Admin, they belong in admin-panel, not portal
        if user.role_id and user.role_id.role_name == 'Admin':
            raise PermissionDenied("Admins must use the Admin Panel, not the Client Portal.")
        return True
        
    actual_decorator = user_passes_test(
        check_is_portal_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
