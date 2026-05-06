from rest_framework.permissions import BasePermission

class IsHRManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='HR Manager').exists()

class IsHROrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return request.user.groups.filter(name='HR Manager').exists()

class IsOwnerOrHR(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='HR Manager').exists():
            return True
        return obj.employee == request.user