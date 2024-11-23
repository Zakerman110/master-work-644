from rest_framework.permissions import BasePermission

from api.serializers import UserSerializer


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        serializer = UserSerializer(user)
        return request.user.is_authenticated and serializer.data['role'] == 'admin'

