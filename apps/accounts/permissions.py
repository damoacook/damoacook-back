from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    인증된 관리자만 접근 가능
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)