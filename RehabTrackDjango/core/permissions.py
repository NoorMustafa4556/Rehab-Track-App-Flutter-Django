from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to Admin users.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role_id):
            return False
        
        # Safe fallback: Check has_permission, but if Role_Permissions table is empty, 
        # it falls back to checking role_name in models.py
        return request.user.has_permission('can_access_admin_panel') or request.user.role_id.role_name == 'Admin'

class IsClinician(permissions.BasePermission):
    """
    Allows access only to Clinician users.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role_id):
            return False
        return request.user.has_permission('can_view_patients') or request.user.role_id.role_name == 'Clinician'

class IsPatient(permissions.BasePermission):
    """
    Allows access only to Patient users.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role_id):
            return False
        return request.user.has_permission('can_view_own_progress') or request.user.role_id.role_name == 'Patient'

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    Only admins can perform write actions.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return request.user.has_permission('can_access_admin_panel') or request.user.role_id.role_name == 'Admin'
