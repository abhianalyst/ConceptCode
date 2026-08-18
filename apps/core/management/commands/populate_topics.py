from django.core.management.base import BaseCommand, CommandError

from apps.core.data.neet_2026_topics import TOPICS
from apps.core.models import Chapter, Topic


class Command(BaseCommand):
    help = "Populate NEET (UG) 2026 syllabus topics."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for subject_name, chapters in TOPICS.items():
            for chapter_name, topic_names in chapters.items():
                try:
                    chapter = Chapter.objects.get(
                        subject__name=subject_name,
                        name=chapter_name,
                    )
                except Chapter.DoesNotExist:
                    raise CommandError(
                        f"Chapter not found: "
                        f"{subject_name} -> {chapter_name}"
                    )

                for topic_name in topic_names:
                    _, was_created = Topic.objects.get_or_create(
                        chapter=chapter,
                        name=topic_name,
                        defaults={
                            "is_active": True,
                        },
                    )

                    if was_created:
                        created += 1
                    else:
                        updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Topic population completed successfully."
            )
        )

        self.stdout.write(
            f"Topics created: {created}"
        )

        self.stdout.write(
            f"Existing topics reused: {updated}"
        )