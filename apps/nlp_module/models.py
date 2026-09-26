from django.db import models


class SearchLog(models.Model):
    """Logs student search queries for analytics."""
    
    query = models.CharField(max_length=500)
    results_count = models.IntegerField(default=0)
    user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.query[:50]} ({self.results_count} results)"