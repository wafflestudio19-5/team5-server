from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import BasePermission, AllowAny
from report.models import ReportedUser


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated and request.user.school_email):
            reported_user = ReportedUser.objects.filter(school_email=request.user.school_email)
            if reported_user.exists():
                reported_user = reported_user[0]
                return timezone.now() > reported_user.updated_at + timedelta(days=30)
            else:
                return True
        else:
            return False


class IsLoggedIn(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)