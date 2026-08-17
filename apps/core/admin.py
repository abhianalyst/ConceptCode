from django.contrib import admin

from .models import Chapter, Subject, Topic


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "subject",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "subject",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "subject__name",
    )

    ordering = (
        "subject",
        "name",
    )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "chapter",
        "subject_name",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "chapter__subject",
        "chapter",
        "is_active",
    )

    search_fields = (
        "unit_number",
        "name",
        "description",
        "chapter__name",
        "chapter__subject__name",
    )

    ordering = (
        "chapter__subject",
        "chapter",
        "name",
    )

    @admin.display(
        description="Subject",
        ordering="chapter__subject",
    )
    def subject_name(self, obj):
        return obj.chapter.subject.name