from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    if detail in action is false, it only checks
    has_permission(),
    if detail in action is false, it checks both
    """
    message = "You do not have the permission to access this object!"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user