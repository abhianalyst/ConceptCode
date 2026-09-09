from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Chapter(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    unit_number = models.PositiveIntegerField(
        default=0,
    )
    name = models.CharField(
        max_length=150,
    )
    description = models.TextField(
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("subject", "unit_number", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("subject", "name"),
                name="unique_chapter_per_subject",
            ),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class Topic(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="topics",
    )
    name = models.CharField(
        max_length=150,
    )
    description = models.TextField(
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("chapter", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("chapter", "name"),
                name="unique_topic_per_chapter",
            ),
        ]

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"


# ============================================================
# QUESTION DIFFICULTY - Defined at module level
# ============================================================

class QuestionDifficulty(models.TextChoices):
    EASY = "Easy", "Easy"
    MEDIUM = "Medium", "Medium"
    HARD = "Hard", "Hard"


# apps/core/models.py - Complete Question model

class Question(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question = models.TextField()
    question_fingerprint = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
    )
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_answer = models.TextField()
    explanation = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=QuestionDifficulty.choices,
        default=QuestionDifficulty.EASY,
    )
    source = models.CharField(
        max_length=500,
    )
    year_tag = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = (
            "topic__chapter__subject",
            "topic__chapter__unit_number",
            "topic__chapter",
            "topic",
            "created_at",
        )

    def __str__(self):
        return self.question

    def get_shuffled_options(self):
        """
        Return shuffled options with the correct answer mapped
        """
        import random
        
        # Original options as list of (label, text)
        original_options = [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d)
        ]
        
        # Shuffle the options
        shuffled = original_options.copy()
        random.shuffle(shuffled)
        
        # Create new options dict with shuffled order
        new_options = {}
        new_correct = None
        
        labels = ['A', 'B', 'C', 'D']
        for i, (old_label, text) in enumerate(shuffled):
            new_label = labels[i]
            new_options[new_label] = text
            if old_label == self.correct_answer:
                new_correct = new_label
        
        return {
            'options': new_options,
            'correct_answer': new_correct,
            'original_correct': self.correct_answer
        }
# ============================================================
# BOOKMARK MODEL
# ============================================================

class Bookmark(models.Model):
    """Model for bookmarked questions."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="bookmarks"
    )
    note = models.TextField(
        blank=True,
        help_text="Optional note about why this question was bookmarked"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ("-created_at",)
        unique_together = ("user", "question")
    
    def __str__(self):
        return f"{self.user.email} - Question #{self.question.id}"


# ============================================================
# QUESTION REPORT MODEL
# ============================================================

class QuestionReport(models.Model):
    """Model for student-reported question issues."""
    
    class ReportType(models.TextChoices):
        WRONG_ANSWER = "wrong_answer", "Wrong Answer"
        INCORRECT_EXPLANATION = "incorrect_explanation", "Incorrect Explanation"
        TYPO = "typo", "Typo/Spelling Error"
        DUPLICATE = "duplicate", "Duplicate Question"
        OTHER = "other", "Other"
    
    class ReportStatus(models.TextChoices):
        PENDING = "pending", "Pending Review"
        REVIEWING = "reviewing", "Under Review"
        RESOLVED = "resolved", "Resolved"
        REJECTED = "rejected", "Rejected"
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="reports"
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_reports"
    )
    report_type = models.CharField(
        max_length=50,
        choices=ReportType.choices
    )
    description = models.TextField(
        help_text="Detailed description of the issue"
    )
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Notes from admin reviewing the report"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_reports"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"Report on {self.question} by {self.reported_by.email}"


# ============================================================
# NOTIFICATION MODEL
# ============================================================

class Notification(models.Model):
    """Model for user notifications."""
    
    class NotificationType(models.TextChoices):
        MILESTONE = "milestone", "Milestone Achieved"
        STREAK = "streak", "Streak Update"
        MOCK_TEST = "mock_test", "New Mock Test Available"
        PRACTICE = "practice", "Practice Reminder"
        ACHIEVEMENT = "achievement", "Achievement Unlocked"
        SYSTEM = "system", "System Update"
        QUIZ = "quiz", "Quiz Result"
        REPORT_RESOLVED = "report_resolved", "Report Resolved"
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Bootstrap icon name (e.g., 'trophy', 'star', 'bell')"
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL to redirect when notification is clicked"
    )
    is_read = models.BooleanField(default=False)
    is_clicked = models.BooleanField(
        default=False,
        help_text="Whether the notification was clicked"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "created_at"]),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"


# ============================================================
# MOCK TEST MODELS
# ============================================================

class MockTest(models.Model):
    """Model for mock tests."""
    
    class TestType(models.TextChoices):
        FULL = "full", "Full NEET Mock"
        SUBJECT = "subject", "Subject Mock"
    
    class SubjectType(models.TextChoices):
        PHYSICS = "physics", "Physics"
        CHEMISTRY = "chemistry", "Chemistry"
        BIOLOGY = "biology", "Biology"
        ALL = "all", "All Subjects"
    
    title = models.CharField(max_length=200)
    test_type = models.CharField(max_length=20, choices=TestType.choices)
    subject_type = models.CharField(max_length=20, choices=SubjectType.choices, default=SubjectType.ALL)
    description = models.TextField(blank=True)
    total_questions = models.IntegerField()
    duration_minutes = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ("-created_at",)
    
    def __str__(self):
        return f"{self.title} ({self.get_test_type_display()})"


class MockTestQuestion(models.Model):
    """Through model for MockTest-Question relationship with ordering."""
    
    mock_test = models.ForeignKey(
        MockTest,
        on_delete=models.CASCADE,
        related_name="mock_test_questions"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="mock_test_questions"
    )
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ("order",)
        unique_together = ("mock_test", "question")
    
    def __str__(self):
        return f"{self.mock_test.title} - Q{self.order}"


class MockTestAttempt(models.Model):
    """Model for tracking student mock test attempts."""
    
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        AUTO_SUBMITTED = "auto_submitted", "Auto-Submitted"
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mock_test_attempts"
    )
    mock_test = models.ForeignKey(
        MockTest,
        on_delete=models.CASCADE,
        related_name="attempts"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    incorrect_count = models.IntegerField(default=0)
    unattempted_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ("-started_at",)
    
    def __str__(self):
        return f"{self.user.email} - {self.mock_test.title}"


class MockTestAnswer(models.Model):
    """Model for storing mock test answers."""
    
    attempt = models.ForeignKey(
        MockTestAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    selected_answer = models.CharField(max_length=10, blank=True)
    is_correct = models.BooleanField(default=False)
    is_marked_for_review = models.BooleanField(default=False)
    time_spent = models.FloatField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("attempt", "question")
    
    def __str__(self):
        return f"Q{self.question.id} - {self.selected_answer}"