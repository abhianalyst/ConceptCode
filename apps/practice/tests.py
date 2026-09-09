from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models import Chapter, Subject, Topic, Question

from .dashboard import get_student_dashboard
from .models import PracticeAttempt, PracticeSession
from django.urls import reverse
from apps.accounts.models import User

User = get_user_model()


class StudentDashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com",
            password="testpass123",
            full_name="Test Student",
        )

        self.subject = Subject.objects.create(
            name="Biology",
        )

        self.chapter = Chapter.objects.create(
            subject=self.subject,
            unit_number=1,
            name="Cell Biology",
        )

        self.topic = Topic.objects.create(
            chapter=self.chapter,
            name="Cell Structure",
        )

        self.question = Question.objects.create(
            topic=self.topic,
            question="What is the basic unit of life?",
            question_fingerprint="a" * 64,
            option_a="Cell",
            option_b="Tissue",
            option_c="Organ",
            option_d="Organism",
            correct_answer="Cell",
            explanation="The cell is the basic unit of life.",
            difficulty="Easy",
            source="test",
        )

    def test_dashboard_requires_user(self):
        with self.assertRaises(ValueError):
            get_student_dashboard(user=None)

    def test_dashboard_returns_empty_statistics(self):
        dashboard = get_student_dashboard(user=self.user)

        self.assertEqual(dashboard["total_sessions"], 0)
        self.assertEqual(dashboard["completed_sessions"], 0)
        self.assertEqual(dashboard["total_attempts"], 0)
        self.assertEqual(dashboard["correct_answers"], 0)
        self.assertEqual(dashboard["incorrect_answers"], 0)
        self.assertEqual(dashboard["accuracy"], 0)
        self.assertEqual(list(dashboard["recent_sessions"]), [])

    def test_dashboard_calculates_statistics(self):
        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer="Cell",
            is_correct=True,
        )

        dashboard = get_student_dashboard(user=self.user)

        self.assertEqual(dashboard["total_sessions"], 1)
        self.assertEqual(dashboard["completed_sessions"], 0)
        self.assertEqual(dashboard["total_attempts"], 1)
        self.assertEqual(dashboard["correct_answers"], 1)
        self.assertEqual(dashboard["incorrect_answers"], 0)
        self.assertEqual(dashboard["accuracy"], 100)

    def test_dashboard_counts_incorrect_answers(self):
        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer="Tissue",
            is_correct=False,
        )

        dashboard = get_student_dashboard(user=self.user)

        self.assertEqual(dashboard["total_attempts"], 1)
        self.assertEqual(dashboard["correct_answers"], 0)
        self.assertEqual(dashboard["incorrect_answers"], 1)
        self.assertEqual(dashboard["accuracy"], 0)

    def test_dashboard_only_includes_current_user(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            full_name="Other Student",
        )

        PracticeSession.objects.create(
            user=other_user,
            topic=self.topic,
        )

        PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        dashboard = get_student_dashboard(user=self.user)

        self.assertEqual(dashboard["total_sessions"], 1)

    def test_dashboard_includes_recent_sessions(self):
        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        dashboard = get_student_dashboard(user=self.user)

        recent_sessions = list(dashboard["recent_sessions"])

        self.assertEqual(len(recent_sessions), 1)
        self.assertEqual(recent_sessions[0].id, session.id)
        self.assertEqual(recent_sessions[0].answered_questions, 0)
        self.assertEqual(recent_sessions[0].correct_questions, 0)

class StudentDashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="dashboard@example.com",
            password="testpass123",
            full_name="Dashboard Student",
        )
        self.client.force_login(self.user)

    def test_dashboard_view_requires_authentication(self):
        self.client.logout()

        response = self.client.get(
            reverse("practice:student-dashboard")
        )

        self.assertEqual(response.status_code, 401)

    def test_dashboard_view_renders_for_authenticated_user(self):
        response = self.client.get(
            reverse("practice:student-dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "practice/student_dashboard.html",
        )
        self.assertContains(
            response,
            "Welcome back, Dashboard Student",
        )