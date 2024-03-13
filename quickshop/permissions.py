from rest_framework.permissions import BasePermission

# class IsAdministratorOrReadOnly(BasePermission):
class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.method in ['GET']:
            return True
        
        # Allow administrators full access
        return request.user.role == 'Administrator'


class IsSalesPersonnel(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.method == 'GET':
            return True
        
        # Allow sales personnel to modify orders
        return request.user.role == 'Sales Personnel'


class IsInventoryManager(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.method == 'GET':
            return True
        
        # Allow inventory managers to modify products
        return request.user.role == 'Inventory Manager'
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.method == 'GET':
            return True
        
        # Allow customers to create orders
        return request.user.role == 'Customer'