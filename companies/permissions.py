from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'owner'):
            if obj.owner == request.user:
                return True
        if hasattr(obj, 'company') and hasattr(obj.company, 'owner'):
            if obj.company.owner == request.user:
                return True
        return False

class IsObjectOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsCompanyMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'company'):
            return obj.company.members.filter(pk=request.user.pk).exists()
        if hasattr(obj, 'members'):
            return obj.members.filter(pk=request.user.pk).exists()
        return False

class IsNotCompanyMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'company'):
            if obj.company.members.filter(pk=request.user.pk).exists():
                return False
        if hasattr(obj, 'members'):
            if obj.members.filter(pk=request.user.pk).exists():
                return False
        return True

class IsNotCompanyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            if obj.owner == request.user:
                return False
        if hasattr(obj, 'company') and hasattr(obj.company, 'owner'):
            if obj.company.owner == request.user:
                return False
        return True

class IsCompanyAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'company'):
            if obj.company.admins.filter(pk=request.user.pk).exists():
                return True
        if hasattr(obj, 'admins'):
            if obj.admins.filter(pk=request.user.pk).exists():
                return True
        return IsOwnerOrReadOnly().has_object_permission(request, view, obj)
