from django.db import models
from django.conf import settings


class Doubt(models.Model):
    """Model for storing student doubts and AI responses."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doubts"
    )
    question = models.TextField(
        max_length=1000,
        help_text="Student's question (max 1000 characters)"
    )
    answer = models.TextField(
        blank=True,
        help_text="AI-generated answer"
    )
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether the doubt was successfully answered"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ("-created_at",)
    
    def __str__(self):
        return f"{self.user.email} - {self.question[:50]}..."

class ConceptExplanation(models.Model):
    """Model for caching AI-generated concept explanations."""
    
    topic = models.OneToOneField(
        'core.Topic',
        on_delete=models.CASCADE,
        related_name='concept_explanation'
    )
    explanation = models.TextField(
        help_text="AI-generated concept explanation"
    )
    generated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(
        default=True,
        help_text="Whether the cached explanation is still valid"
    )
    
    class Meta:
        ordering = ("-generated_at",)
    
    def __str__(self):
        return f"Explanation for {self.topic.name}"
    
    def is_expired(self):
        """Check if cache is older than 24 hours."""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.generated_at > timedelta(hours=24)