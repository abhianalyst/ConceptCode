# apps/core/services/notification_service.py

from django.utils import timezone
from django.db import transaction
from apps.core.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationService:
    """Service for creating and managing notifications."""
    
    @staticmethod
    def create_notification(user, notification_type, title, message, icon="", link=""):
        """Create a single notification for a user."""
        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            icon=icon,
            link=link,
        )
    
    @staticmethod
    def create_bulk_notification(users, notification_type, title, message, icon="", link=""):
        """Create notifications for multiple users."""
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    icon=icon,
                    link=link,
                )
            )
        return Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for a user."""
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).count()
    
    @staticmethod
    def get_notifications(user, limit=50, include_read=False):
        """Get notifications for a user."""
        queryset = Notification.objects.filter(user=user)
        if not include_read:
            queryset = queryset.filter(is_read=False)
        return queryset[:limit]
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user."""
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a specific notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def delete_old_notifications(days=30):
        """Delete notifications older than specified days."""
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return Notification.objects.filter(created_at__lt=cutoff).delete()


# ============================================================
# MILESTONE & STREAK DETECTION
# ============================================================

class MilestoneDetector:
    """Detect and create milestone notifications."""
    
    MILESTONES = {
        10: "10 Questions Attempted",
        25: "25 Questions Attempted", 
        50: "50 Questions Attempted",
        100: "100 Questions Attempted",
        250: "250 Questions Attempted",
        500: "500 Questions Attempted",
        1000: "1000 Questions Attempted!",
    }
    
    @staticmethod
    def check_milestones(user, total_attempts):
        """Check if user has reached any new milestone."""
        from apps.core.models import Notification
        
        # Get existing milestone notifications for this user
        existing_milestones = Notification.objects.filter(
            user=user,
            notification_type=Notification.NotificationType.MILESTONE
        ).values_list('title', flat=True)
        
        created_notifications = []
        
        for threshold, title in MilestoneDetector.MILESTONES.items():
            if total_attempts >= threshold:
                milestone_key = f"milestone_{threshold}"
                # Check if this milestone notification already exists
                if not any(milestone_key in existing for existing in existing_milestones):
                    notification = NotificationService.create_notification(
                        user=user,
                        notification_type=Notification.NotificationType.MILESTONE,
                        title=f"🎉 {title}!",
                        message=f"Congratulations! You have successfully attempted {threshold} questions. Keep up the great work!",
                        icon="trophy",
                        link="/practice/dashboard/"
                    )
                    created_notifications.append(notification)
        
        return created_notifications
    
    @staticmethod
    def check_streak(user, streak_days):
        """Check and create streak notifications."""
        from apps.core.models import Notification
        
        streak_milestones = [3, 7, 14, 21, 30, 60, 90, 180, 365]
        
        created_notifications = []
        
        for milestone in streak_milestones:
            if streak_days == milestone:
                notification = NotificationService.create_notification(
                    user=user,
                    notification_type=Notification.NotificationType.STREAK,
                    title=f"🔥 {milestone}-Day Streak!",
                    message=f"Amazing! You've practiced for {milestone} consecutive days. Your consistency is inspiring!",
                    icon="fire",
                    link="/practice/dashboard/"
                )
                created_notifications.append(notification)
                break
            elif streak_days > milestone:
                # Check if we already sent notification for this milestone
                existing = Notification.objects.filter(
                    user=user,
                    notification_type=Notification.NotificationType.STREAK,
                    title__icontains=f"{milestone}-Day"
                ).exists()
                if not existing:
                    notification = NotificationService.create_notification(
                        user=user,
                        notification_type=Notification.NotificationType.STREAK,
                        title=f"🔥 {milestone}-Day Streak!",
                        message=f"Amazing! You've practiced for {milestone} consecutive days. Your consistency is inspiring!",
                        icon="fire",
                        link="/practice/dashboard/"
                    )
                    created_notifications.append(notification)
        
        return created_notifications


# ============================================================
# MOCK TEST NOTIFICATIONS
# ============================================================

class MockTestNotifier:
    """Send notifications for new mock tests."""
    
    @staticmethod
    def notify_new_mock_test(test_name, description, link):
        """Notify all students about a new mock test."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        students = User.objects.filter(role='student', is_active=True)
        
        notifications = NotificationService.create_bulk_notification(
            users=students,
            notification_type=Notification.NotificationType.MOCK_TEST,
            title=f"📝 New Mock Test Available: {test_name}",
            message=f"{description} - Take the test now to assess your preparation!",
            icon="file-earmark-check",
            link=link
        )
        
        return notifications