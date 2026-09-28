"""
Study Planner service layer.

Generates a personalized day-by-day study plan that:
1. Prioritizes weak topics (via ML WeakAreaDetector)
2. Fills remaining slots with unstarted topics (via syllabus)
3. Distributes tasks across days until exam date
4. Reserves ~20% buffer for revision/mock tests
"""

import logging
from datetime import timedelta
from math import ceil

from django.db import transaction
from django.utils import timezone

from apps.core.models import Topic
from apps.practice.models import PracticeAttempt
from apps.ml_module.services import WeakAreaDetector

from .models import StudyPlan, StudyTask

logger = logging.getLogger(__name__)


class StudyPlanner:
    """Generates and regenerates study plans."""

    WEAK_TOPIC_LIMIT = 15          # top N weak topics to prioritize
    BUFFER_RATIO = 0.20            # 20% of slots reserved
    TASK_DURATION_MINUTES = 45     # default per-topic session length
    MAX_DAYS = 180                 # hard cap on plan length

    @classmethod
    @transaction.atomic
    def generate_plan(cls, user, exam_date, daily_hours):
        """
        Create a fresh StudyPlan for the user, deleting any existing active plan.
        Returns the new StudyPlan instance.
        """
        # Deactivate old plans
        StudyPlan.objects.filter(user=user, is_active=True).update(is_active=False)

        plan = StudyPlan.objects.create(
            user=user,
            exam_date=exam_date,
            daily_hours=daily_hours,
            is_active=True,
        )

        tasks_created = cls._build_schedule(plan)
        logger.info(
            "Generated study plan #%s for %s: %s tasks across %s days",
            plan.id, user.email, tasks_created, plan.days_remaining,
        )
        return plan

    @classmethod
    def _build_schedule(cls, plan):
        """Compute and persist tasks for the plan."""

        today = timezone.localdate()
        days_available = min((plan.exam_date - today).days, cls.MAX_DAYS)

        if days_available <= 0:
            logger.warning("Plan for %s has no future days.", plan.user.email)
            return 0

        # Effective working days after buffer
        effective_days = max(int(days_available * (1 - cls.BUFFER_RATIO)), 1)

        # How many tasks fit per day? (daily_hours * 60 / task_duration)
        tasks_per_day = max((plan.daily_hours * 60) // cls.TASK_DURATION_MINUTES, 1)
        total_slots = effective_days * tasks_per_day

        # Build the prioritized topic queue
        queue = cls._prioritized_topics(plan.user)

        if not queue:
            logger.warning("No topics available to schedule for %s.", plan.user.email)
            return 0

        # Cap queue to fit available slots
        queue = queue[:total_slots]

        # Assign each topic to a day
        tasks_created = 0
        slot_index = 0
        for entry in queue:
            day_offset = slot_index // tasks_per_day
            scheduled_date = today + timedelta(days=day_offset)

            StudyTask.objects.create(
                plan=plan,
                topic=entry["topic"],
                scheduled_date=scheduled_date,
                duration_minutes=cls.TASK_DURATION_MINUTES,
                priority=entry["priority"],
                reason=entry["reason"],
            )
            tasks_created += 1
            slot_index += 1

        return tasks_created

    @classmethod
    def _prioritized_topics(cls, user):
        """
        Return a list of dicts: {'topic', 'priority', 'reason'}
        ordered by: weak-first, then unstarted, then in-progress.
        """
        entries = []
        seen_topic_ids = set()

        # 1. Weak topics from ML
        try:
            weak_topics = WeakAreaDetector.get_weak_topics(
                user, limit=cls.WEAK_TOPIC_LIMIT
            )
        except Exception as exc:
            logger.exception("WeakAreaDetector failed: %s", exc)
            weak_topics = []

        for perf in weak_topics:
            topic = getattr(perf, "topic", None)
            if topic is None or topic.id in seen_topic_ids:
                continue
            seen_topic_ids.add(topic.id)
            entries.append({
                "topic": topic,
                "priority": StudyTask.Priority.HIGH,
                "reason": f"AI weak area — {getattr(perf, 'accuracy', 0):.0f}% accuracy",
            })

        # 2. Unstarted topics from the syllabus
        all_topics = Topic.objects.filter(is_active=True).select_related(
            "chapter", "chapter__subject"
        )
        for topic in all_topics:
            if topic.id in seen_topic_ids:
                continue
            if not topic.questions.filter(is_active=True).exists():
                continue  # skip topics with no questions

            attempted = PracticeAttempt.objects.filter(
                session__user=user, session__topic=topic
            ).exists()

            if not attempted:
                seen_topic_ids.add(topic.id)
                entries.append({
                    "topic": topic,
                    "priority": StudyTask.Priority.MEDIUM,
                    "reason": "Not yet started",
                })

        # 3. In-progress topics (attempted but not completed)
        for topic in all_topics:
            if topic.id in seen_topic_ids:
                continue

            total_q = topic.questions.filter(is_active=True).count()
            attempted_q = (
                PracticeAttempt.objects
                .filter(session__user=user, session__topic=topic)
                .values("question")
                .distinct()
                .count()
            )
            if total_q > 0 and attempted_q < total_q:
                seen_topic_ids.add(topic.id)
                entries.append({
                    "topic": topic,
                    "priority": StudyTask.Priority.LOW,
                    "reason": f"In progress — {attempted_q}/{total_q} attempted",
                })

        return entries


class StudyTaskService:
    """Operations on individual tasks."""

    @staticmethod
    def mark_completed(task_id, user):
        task = StudyTask.objects.filter(id=task_id, plan__user=user).first()
        if not task:
            return None
        task.mark_completed()
        return task

    @staticmethod
    def mark_skipped(task_id, user):
        task = StudyTask.objects.filter(id=task_id, plan__user=user).first()
        if not task:
            return None
        task.mark_skipped()
        return task

    @staticmethod
    def todays_tasks(plan):
        today = timezone.localdate()
        return plan.tasks.filter(scheduled_date=today).order_by("-priority", "id")

    @staticmethod
    def upcoming_tasks(plan, days=7):
        today = timezone.localdate()
        end = today + timedelta(days=days)
        return plan.tasks.filter(
            scheduled_date__gt=today,
            scheduled_date__lte=end,
        ).order_by("scheduled_date", "-priority")