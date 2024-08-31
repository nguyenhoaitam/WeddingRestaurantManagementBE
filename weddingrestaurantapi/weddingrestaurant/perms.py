from rest_framework import permissions


class FeedbackOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, feedback):
        return super().has_permission(request, view) and request.user == feedback.customer.user
