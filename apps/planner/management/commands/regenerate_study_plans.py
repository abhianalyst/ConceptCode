"""Nightly command: regenerate plans so new weak areas get picked up."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.planner.models import StudyPlan
from apps.planner.services import StudyPlanner


class Command(BaseCommand):
    help = "Regenerate all active study plans (run nightly)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="Only regenerate for this user's email.",
        )

    def handle(self, *args, **options):
        qs = StudyPlan.objects.filter(is_active=True)
        if options["user"]:
            qs = qs.filter(user__email=options["user"])

        count = 0
        for plan in qs:
            try:
                StudyPlanner.generate_plan(
                    user=plan.user,
                    exam_date=plan.exam_date,
                    daily_hours=plan.daily_hours,
                )
                count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Regenerated plan for {plan.user.email}"))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"✗ Failed for {plan.user.email}: {exc}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {count} plan(s) regenerated at {timezone.now():%Y-%m-%d %H:%M}."
        ))