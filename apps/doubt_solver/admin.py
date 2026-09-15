from django.contrib import admin
from .models import ConceptExplanation, Doubt


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

@admin.register(ConceptExplanation)
class ConceptExplanationAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'generated_at', 'is_valid', 'is_expired_display')
    list_filter = ('is_valid', 'generated_at')
    search_fields = ('topic__name', 'topic__chapter__name')
    readonly_fields = ('generated_at',)
    ordering = ('-generated_at',)
    
    def is_expired_display(self, obj):
        return "Yes" if obj.is_expired() else "No"
    is_expired_display.short_description = 'Cache Expired'