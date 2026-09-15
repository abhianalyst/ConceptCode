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