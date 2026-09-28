from django.conf import settings
from django.db import models
from django.utils import timezone


class StudyPlan(models.Model):
    """A student's personalized study plan leading up to the NEET exam."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_plans",
    )
    exam_date = models.DateField(help_text="Target NEET exam date")
    daily_hours = models.PositiveSmallIntegerField(
        default=4,
        help_text="Target study hours per day",
    )
    is_active = models.BooleanField(default=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.email} → NEET {self.exam_date}"

    @property
    def days_remaining(self):
        delta = self.exam_date - timezone.localdate()
        return max(delta.days, 0)

    @property
    def total_tasks(self):
        return self.tasks.count()

    @property
    def completed_tasks(self):
        return self.tasks.filter(status=StudyTask.Status.COMPLETED).count()

    @property
    def progress_percent(self):
        total = self.total_tasks
        if total == 0:
            return 0
        return round((self.completed_tasks / total) * 100, 1)


class StudyTask(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    class Priority(models.TextChoices):
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    topic = models.ForeignKey(
        "core.Topic",
        on_delete=models.CASCADE,
        related_name="study_tasks",
    )
    scheduled_date = models.DateField()
    duration_minutes = models.PositiveSmallIntegerField(default=45)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Why this task was scheduled (e.g., weak area, unstarted topic)",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_date", "-priority", "id"]
        indexes = [
            models.Index(fields=["plan", "scheduled_date"]),
            models.Index(fields=["plan", "status"]),
        ]

    def __str__(self):
        return f"{self.scheduled_date} — {self.topic.name}"

    def mark_completed(self):
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def mark_skipped(self):
        self.status = self.Status.SKIPPED
        self.save(update_fields=["status"])