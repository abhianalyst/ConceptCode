# apps/accounts/context_processors.py

from django.db import OperationalError
from apps.core.models import Notification


def pending_reports_count(request):
    """Add pending reports count to all templates."""
    if request.user.is_authenticated and (
        request.user.role == 'admin' or 
        request.user.is_staff or 
        request.user.is_superuser
    ):
        try:
            from apps.core.models import QuestionReport
            count = QuestionReport.objects.filter(
                status=QuestionReport.ReportStatus.PENDING
            ).count()
            return {'pending_reports': count}
        except (OperationalError, ImportError):
            return {'pending_reports': 0}
    return {'pending_reports': 0}


def notification_count(request):
    """Add unread notification count to all templates."""
    if request.user.is_authenticated:
        try:
            from apps.core.models import Notification
            count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
            return {'unread_notification_count': count}
        except (OperationalError, ImportError):
            return {'unread_notification_count': 0}
    return {'unread_notification_count': 0}