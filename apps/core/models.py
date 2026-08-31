from django.db import models


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

class QuestionDifficulty(models.TextChoices):
    EASY = "Easy", "Easy"
    MEDIUM = "Medium", "Medium"
    HARD = "Hard", "Hard"

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