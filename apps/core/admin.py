from django.contrib import admin

from .models import Chapter, Question, Subject, Topic


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
        "unit_number",
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
        "unit_number",
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
        "name",
        "description",
        "chapter__name",
        "chapter__subject__name",
    )

    ordering = (
        "chapter__subject",
        "chapter__unit_number",
        "chapter__name",
        "name",
    )

    @admin.display(
        description="Subject",
        ordering="chapter__subject",
    )
    def subject_name(self, obj):
        return obj.chapter.subject.name

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "topic",
        "subject_name",
        "chapter_name",
        "difficulty",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "difficulty",
        "is_active",
        "topic__chapter__subject",
        "topic__chapter",
        "topic",
    )

    search_fields = (
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "explanation",
        "source",
        "topic__name",
        "topic__chapter__name",
        "topic__chapter__subject__name",
    )

    ordering = (
        "topic__chapter__subject",
        "topic__chapter__unit_number",
        "topic__chapter",
        "topic",
        "created_at",
    )

    readonly_fields = (
        "question_fingerprint",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Question",
            {
                "fields": (
                    "topic",
                    "question",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                    "explanation",
                    "difficulty",
                ),
            },
        ),
        (
            "Source",
            {
                "fields": (
                    "source",
                    "year_tag",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                ),
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "question_fingerprint",
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    list_per_page = 50

    @admin.display(
        description="Subject",
        ordering="topic__chapter__subject",
    )
    def subject_name(self, obj):
        return obj.topic.chapter.subject.name

    @admin.display(
        description="Chapter",
        ordering="topic__chapter",
    )
    def chapter_name(self, obj):
        return obj.topic.chapter.name