# products/permissions.py
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only authenticated staff (admin) users to
    create, update, or delete objects. Read access is allowed to any user.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsAuthenticatedOrPurchase(permissions.BasePermission):
    """
    Custom permission for purchasing actions (e.g., adding to cart, checkout).
    Requires the user to be authenticated. (Will be used for future cart/order models)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return True