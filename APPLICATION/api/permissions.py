from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or
                request.user == obj.IDAutor or
                request.user.Profile.IDResponsibilityGroup
                )


class SetRatingPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.IDAutor
