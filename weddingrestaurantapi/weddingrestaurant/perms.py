from rest_framework import permissions
from rest_framework.permissions import BasePermission


class FeedbackOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, feedback):
        return super().has_permission(request, view) and request.user == feedback.customer.user


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role.name == 'admin'


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role.name == 'staff'