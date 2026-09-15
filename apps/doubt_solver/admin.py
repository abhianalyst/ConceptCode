from django.contrib import admin
from .models import Doubt


@admin.register(Doubt)
class DoubtAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question_preview', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('user__email', 'question', 'answer')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def question_preview(self, obj):
        return obj.question[:80] + ('...' if len(obj.question) > 80 else '')
    question_preview.short_description = 'Question'