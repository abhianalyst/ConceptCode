from django.contrib import admin

from .models import StudyPlan, StudyTask


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "exam_date", "daily_hours", "is_active", "total_tasks", "progress_percent")
    list_filter = ("is_active", "exam_date")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("generated_at", "updated_at")


@admin.register(StudyTask)
class StudyTaskAdmin(admin.ModelAdmin):
    list_display = ("plan", "topic", "scheduled_date", "priority", "status", "duration_minutes")
    list_filter = ("status", "priority", "scheduled_date")
    search_fields = ("topic__name", "plan__user__email")
    autocomplete_fields = ("topic",)