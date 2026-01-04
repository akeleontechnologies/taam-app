from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows access to owners or admin users.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.is_staff:
            return True
        
        # Check if object has 'owner' attribute
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Check if object has 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Default to user ID comparison
        return obj == request.user


class CanViewOwnAccount(permissions.BasePermission):
    """Permission to allow users to view their own account"""

    def has_permission(self, request, view):
        if view.action != "list":
            return True

        if not request.user.is_staff:
            return True

        return False

    def has_object_permission(self, request, view, account):
        if request.user.is_staff:
            return True

        if account == request.user:
            return True

        return False


class IsCompanyUser(permissions.BasePermission):
    """Permission for company users"""

    def has_permission(self, request, view):
        if request.user.user_type == 'company':
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        # Add specific object-level permissions based on your models
        # For example, if you have Company model:
        # if hasattr(obj, 'company'):
        #     return obj.company.user == request.user
        
        return False


class IsEmployeeUser(permissions.BasePermission):
    """Permission for employee users"""

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'employee'
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        # Add specific object-level permissions based on your models
        # For example, if you have Employee model:
        # if hasattr(obj, 'employee'):
        #     return obj.employee.user == request.user
        
        return False


class IsEmployeeAdminUser(permissions.BasePermission):
    """Permission for employee admin users"""

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'employee_admin'
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        # Employee admins can manage employees in their company
        # Add specific logic based on your business rules
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow owners of an object to edit it"""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to allow owners or admins to access an object"""

    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.is_staff:
            return True

        # Check if the object has an owner field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Fallback to user field
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False

