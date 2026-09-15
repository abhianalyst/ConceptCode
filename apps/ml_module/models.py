from django.db import models
from django.conf import settings


class TopicPerformance(models.Model):
    """Stores ML-predicted performance classification for each topic."""
    
    class Classification(models.TextChoices):
        STRONG = "Strong", "Strong"
        MODERATE = "Moderate", "Moderate"
        WEAK = "Weak", "Weak"
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topic_performances"
    )
    topic = models.ForeignKey(
        'core.Topic',
        on_delete=models.CASCADE,
        related_name="performances"
    )
    
    # Features used for classification
    accuracy = models.FloatField(default=0.0)
    attempts = models.IntegerField(default=0)
    avg_time = models.FloatField(default=0.0)
    easy_accuracy = models.FloatField(default=0.0)
    medium_accuracy = models.FloatField(default=0.0)
    hard_accuracy = models.FloatField(default=0.0)
    
    # ML classification
    classification = models.CharField(
        max_length=20,
        choices=Classification.choices,
        default=Classification.MODERATE
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Confidence score of prediction (0-1)"
    )
    
    # Recommendation priority
    priority = models.IntegerField(
        default=0,
        help_text="Higher = more urgent to practice"
    )
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "topic")
        ordering = ("-priority", "-last_updated")
        indexes = [
            models.Index(fields=["user", "classification"]),
            models.Index(fields=["user", "-priority"]),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.topic.name} ({self.classification})"
    
    @property
    def needs_attention(self):
        return self.classification in [self.Classification.WEAK, self.Classification.MODERATE]