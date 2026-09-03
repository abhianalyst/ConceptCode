from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models import Question, Subject, Chapter, Topic
from .models import PracticeAttempt, PracticeSession


class PracticeModelTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="practice@test.com",
            password="test-password",
            full_name="Practice Test User",
        )

        self.subject = Subject.objects.create(
            name="Practice Test Biology",
        )

        self.chapter = Chapter.objects.create(
            subject=self.subject,
            unit_number=1,
            name="Practice Test Chapter",
        )

        self.topic = Topic.objects.create(
            chapter=self.chapter,
            name="Practice Test Topic",
        )

        self.question = Question.objects.create(
            topic=self.topic,
            question="What is the test answer?",
            question_fingerprint="a" * 64,
            option_a="Answer A",
            option_b="Answer B",
            option_c="Answer C",
            option_d="Answer D",
            correct_answer="Answer A",
            explanation="Test explanation.",
            difficulty="Easy",
            source="practice_test",
        )

    def test_create_practice_session(self):
        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        self.assertEqual(session.user, self.user)
        self.assertEqual(session.topic, self.topic)
        self.assertEqual(
            session.status,
            PracticeSession.Status.ACTIVE,
        )
        self.assertIsNone(session.completed_at)

    def test_create_practice_attempt(self):
        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        attempt = PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer="Answer A",
            is_correct=True,
        )

        self.assertEqual(attempt.session, session)
        self.assertEqual(attempt.question, self.question)
        self.assertEqual(attempt.selected_answer, "Answer A")
        self.assertTrue(attempt.is_correct)

    def test_session_can_access_attempts(self):
        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer="Answer B",
            is_correct=False,
        )

        self.assertEqual(
            session.attempts.count(),
            1,
        )
    
    def test_create_session_service(self):
        from .services import create_practice_session

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        self.assertEqual(session.user, self.user)
        self.assertEqual(session.topic, self.topic)
        self.assertEqual(
            session.status,
            PracticeSession.Status.ACTIVE,
        )

    def test_create_session_requires_user(self):
        from .services import create_practice_session

        with self.assertRaises(ValueError):
            create_practice_session(
                user=None,
                topic=self.topic,
            )

    def test_create_session_requires_topic(self):
        from .services import create_practice_session

        with self.assertRaises(ValueError):
            create_practice_session(
                user=self.user,
                topic=None,
            )
    
    def test_get_next_question_returns_unanswered_question(self):
        from .services import (
            create_practice_session,
            get_next_question,
        )

        question_2 = Question.objects.create(
            topic=self.topic,
            question="What is the second test answer?",
            question_fingerprint="b" * 64,
            option_a="Answer A",
            option_b="Answer B",
            option_c="Answer C",
            option_d="Answer D",
            correct_answer="Answer B",
            explanation="Second test explanation.",
            difficulty="Medium",
            source="practice_test",
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        next_question = get_next_question(session=session)

        self.assertEqual(next_question, self.question)

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer="Answer A",
            is_correct=True,
        )

        next_question = get_next_question(session=session)

        self.assertEqual(next_question, question_2)

    def test_get_next_question_returns_none_when_all_answered(self):
        from .services import (
            create_practice_session,
            get_next_question,
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer="Answer A",
            is_correct=True,
        )

        self.assertIsNone(
            get_next_question(session=session),
        )

    def test_get_next_question_ignores_inactive_questions(self):
        from .services import (
            create_practice_session,
            get_next_question,
        )

        self.question.is_active = False
        self.question.save(update_fields=["is_active"])

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        self.assertIsNone(
            get_next_question(session=session),
        )

    def test_get_next_question_requires_session(self):
        from .services import get_next_question

        with self.assertRaises(ValueError):
            get_next_question(session=None)
    
    def test_submit_correct_answer(self):
        from .services import (
            create_practice_session,
            submit_answer,
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        attempt = submit_answer(
            session=session,
            question=self.question,
            selected_answer="Answer A",
        )

        self.assertEqual(attempt.session, session)
        self.assertEqual(attempt.question, self.question)
        self.assertEqual(attempt.selected_answer, "Answer A")
        self.assertTrue(attempt.is_correct)

    def test_submit_incorrect_answer(self):
        from .services import (
            create_practice_session,
            submit_answer,
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        attempt = submit_answer(
            session=session,
            question=self.question,
            selected_answer="Answer B",
        )

        self.assertFalse(attempt.is_correct)

    def test_submit_answer_requires_selected_answer(self):
        from .services import (
            create_practice_session,
            submit_answer,
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        with self.assertRaises(ValueError):
            submit_answer(
                session=session,
                question=self.question,
                selected_answer="",
            )

    def test_submit_answer_rejects_question_from_other_topic(self):
        from .services import (
            create_practice_session,
            submit_answer,
        )

        other_topic = Topic.objects.create(
            chapter=self.chapter,
            name="Other Practice Topic",
        )

        other_question = Question.objects.create(
            topic=other_topic,
            question="What is another test question?",
            question_fingerprint="c" * 64,
            option_a="Answer A",
            option_b="Answer B",
            option_c="Answer C",
            option_d="Answer D",
            correct_answer="Answer A",
            explanation="Another test explanation.",
            difficulty="Easy",
            source="practice_test",
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        with self.assertRaises(ValueError):
            submit_answer(
                session=session,
                question=other_question,
                selected_answer="Answer A",
            )

    def test_submit_answer_rejects_duplicate_attempt(self):
        from .services import (
            create_practice_session,
            submit_answer,
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        submit_answer(
            session=session,
            question=self.question,
            selected_answer="Answer A",
        )

        with self.assertRaises(ValueError):
            submit_answer(
                session=session,
                question=self.question,
                selected_answer="Answer A",
            )

    def test_submit_answer_requires_session(self):
        from .services import submit_answer

        with self.assertRaises(ValueError):
            submit_answer(
                session=None,
                question=self.question,
                selected_answer="Answer A",
            )

    def test_submit_answer_requires_question(self):
        from .services import submit_answer

        with self.assertRaises(ValueError):
            submit_answer(
                session=None,
                question=None,
                selected_answer="Answer A",
            )

    def test_complete_practice_session_marks_completed(self):
        from apps.practice.services import complete_practice_session

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        completed = complete_practice_session(session=session)

        completed.refresh_from_db()

        self.assertEqual(completed.status, PracticeSession.Status.COMPLETED)
        self.assertIsNotNone(completed.completed_at)


    def test_complete_practice_session_requires_session(self):
        from apps.practice.services import complete_practice_session

        with self.assertRaises(ValueError):
            complete_practice_session(session=None)


    def test_complete_practice_session_is_idempotent(self):
        from apps.practice.services import complete_practice_session

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        completed = complete_practice_session(session=session)
        original_completed_at = completed.completed_at

        completed_again = complete_practice_session(session=completed)

        completed_again.refresh_from_db()

        self.assertEqual(
            completed_again.status,
            PracticeSession.Status.COMPLETED,
        )
        self.assertEqual(
            completed_again.completed_at,
            original_completed_at,
        )

    def test_get_practice_progress_initial(self):
        from apps.practice.progress import get_practice_progress

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        progress = get_practice_progress(session=session)

        self.assertEqual(progress["total_questions"], 1)
        self.assertEqual(progress["answered_questions"], 0)
        self.assertEqual(progress["remaining_questions"], 1)
        self.assertEqual(progress["correct_answers"], 0)
        self.assertEqual(progress["incorrect_answers"], 0)
        self.assertEqual(progress["percentage"], 0)


    def test_get_practice_progress_after_answer(self):
        from apps.practice.progress import get_practice_progress

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer=self.question.correct_answer,
            is_correct=True,
        )

        progress = get_practice_progress(session=session)

        self.assertEqual(progress["total_questions"], 1)
        self.assertEqual(progress["answered_questions"], 1)
        self.assertEqual(progress["remaining_questions"], 0)
        self.assertEqual(progress["correct_answers"], 1)
        self.assertEqual(progress["incorrect_answers"], 0)
        self.assertEqual(progress["percentage"], 100)


    def test_get_practice_progress_incorrect_answer(self):
        from apps.practice.progress import get_practice_progress

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer="Wrong answer",
            is_correct=False,
        )

        progress = get_practice_progress(session=session)

        self.assertEqual(progress["correct_answers"], 0)
        self.assertEqual(progress["incorrect_answers"], 1)
        self.assertEqual(progress["percentage"], 100)


    def test_get_practice_progress_requires_session(self):
        from apps.practice.progress import get_practice_progress

        with self.assertRaises(ValueError):
            get_practice_progress(session=None)

    def test_create_session_view(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        response = client.post(
            f"/practice/topics/{self.topic.id}/sessions/",
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()

        self.assertIn("session_id", data)
        self.assertEqual(data["topic_id"], self.topic.id)
        self.assertEqual(data["status"], PracticeSession.Status.ACTIVE)


    def test_create_session_view_requires_authentication(self):
        from django.test import Client

        client = Client()

        response = client.post(
            f"/practice/topics/{self.topic.id}/sessions/",
        )

        self.assertEqual(response.status_code, 401)


    def test_create_session_view_invalid_topic(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        response = client.post(
            "/practice/topics/999999/sessions/",
        )

        self.assertEqual(response.status_code, 404)


    def test_create_session_view_requires_post(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        response = client.get(
            f"/practice/topics/{self.topic.id}/sessions/",
        )

        self.assertEqual(response.status_code, 405)

    def test_next_question_view(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/next/",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["question_id"], self.question.id)
        self.assertEqual(data["question"], self.question.question)
        self.assertEqual(
            data["options"],
            [
                self.question.option_a,
                self.question.option_b,
                self.question.option_c,
                self.question.option_d,
            ],
        )
        self.assertEqual(data["difficulty"], self.question.difficulty)
        self.assertNotIn("correct_answer", data)


    def test_next_question_view_requires_authentication(self):
        from django.test import Client

        client = Client()

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/next/",
        )

        self.assertEqual(response.status_code, 401)


    def test_next_question_view_rejects_other_users_session(self):
        from django.contrib.auth import get_user_model
        from django.test import Client

        User = get_user_model()

        other_user = User.objects.create_user(
            email="other-practice@test.com",
            password="testpass123",
            full_name="Other Practice User",
        )

        session = PracticeSession.objects.create(
            user=other_user,
            topic=self.topic,
        )

        client = Client()
        client.force_login(self.user)

        response = client.get(
            f"/practice/sessions/{session.id}/next/",
        )

        self.assertEqual(response.status_code, 404)


    def test_next_question_view_no_questions_remaining(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer=self.question.correct_answer,
            is_correct=True,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/next/",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "no questions remaining"},
        )


    def test_next_question_view_requires_get(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/next/",
        )

        self.assertEqual(response.status_code, 405)

    def test_submit_session_answer_view_correct(self):
        from django.test import Client
        import json

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": self.question.id,
                "selected_answer": self.question.correct_answer,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()

        self.assertIn("attempt_id", data)
        self.assertEqual(data["question_id"], self.question.id)
        self.assertEqual(
            data["selected_answer"],
            self.question.correct_answer,
        )
        self.assertTrue(data["is_correct"])


    def test_submit_session_answer_view_incorrect(self):
        from django.test import Client
        import json

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": self.question.id,
                "selected_answer": "Wrong answer",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()

        self.assertFalse(data["is_correct"])


    def test_submit_session_answer_view_requires_authentication(self):
        from django.test import Client
        import json

        client = Client()

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": self.question.id,
                "selected_answer": self.question.correct_answer,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)


    def test_submit_session_answer_view_invalid_json(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data="not valid json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "invalid JSON",
        )


    def test_submit_session_answer_view_missing_question_id(self):
        from django.test import Client
        import json

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "selected_answer": self.question.correct_answer,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "question_id is required",
        )


    def test_submit_session_answer_view_missing_selected_answer(self):
        from django.test import Client
        import json

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": self.question.id,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "selected_answer is required",
        )


    def test_submit_session_answer_view_question_not_found(self):
        from django.test import Client
        import json

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": 999999,
                "selected_answer": "Anything",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)


    def test_submit_session_answer_view_rejects_other_users_session(self):
        from django.contrib.auth import get_user_model
        from django.test import Client
        import json

        User = get_user_model()

        other_user = User.objects.create_user(
            email="answer-other@test.com",
            password="testpass123",
            full_name="Answer Other User",
        )

        session = PracticeSession.objects.create(
            user=other_user,
            topic=self.topic,
        )

        client = Client()
        client.force_login(self.user)

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": self.question.id,
                "selected_answer": self.question.correct_answer,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)


    def test_submit_session_answer_view_rejects_wrong_topic_question(self):
        from django.test import Client
        from apps.core.models import Chapter, Subject, Topic
        import json

        other_subject = Subject.objects.create(
            name="Other Answer Subject",
        )
        other_chapter = Chapter.objects.create(
            subject=other_subject,
            unit_number=2,
            name="Other Answer Chapter",
        )
        other_topic = Topic.objects.create(
            chapter=other_chapter,
            name="Other Answer Topic",
        )

        other_question = Question.objects.create(
            topic=other_topic,
            question="Other topic question?",
            question_fingerprint="b" * 64,
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            explanation="Explanation",
            difficulty="Easy",
            source="test",
        )

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": other_question.id,
                "selected_answer": "A",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "question does not belong to session topic",
        )


    def test_submit_session_answer_view_rejects_duplicate_answer(self):
        from django.test import Client
        import json

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer=self.question.correct_answer,
            is_correct=True,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/answer/",
            data=json.dumps({
                "question_id": self.question.id,
                "selected_answer": self.question.correct_answer,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "question has already been answered",
        )


    def test_submit_session_answer_view_requires_post(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/answer/",
        )

        self.assertEqual(response.status_code, 405)

    def test_session_progress_view(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/progress/",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["total_questions"], 1)
        self.assertEqual(data["answered_questions"], 0)
        self.assertEqual(data["remaining_questions"], 1)
        self.assertEqual(data["correct_answers"], 0)
        self.assertEqual(data["incorrect_answers"], 0)
        self.assertEqual(data["percentage"], 0)


    def test_session_progress_view_after_answer(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        PracticeAttempt.objects.create(
            session=session,
            question=self.question,
            selected_answer=self.question.correct_answer,
            is_correct=True,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/progress/",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["total_questions"], 1)
        self.assertEqual(data["answered_questions"], 1)
        self.assertEqual(data["remaining_questions"], 0)
        self.assertEqual(data["correct_answers"], 1)
        self.assertEqual(data["incorrect_answers"], 0)
        self.assertEqual(data["percentage"], 100)


    def test_session_progress_view_requires_authentication(self):
        from django.test import Client

        client = Client()

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/progress/",
        )

        self.assertEqual(response.status_code, 401)


    def test_session_progress_view_rejects_other_users_session(self):
        from django.contrib.auth import get_user_model
        from django.test import Client

        User = get_user_model()

        other_user = User.objects.create_user(
            email="progress-other@test.com",
            password="testpass123",
            full_name="Progress Other User",
        )

        session = PracticeSession.objects.create(
            user=other_user,
            topic=self.topic,
        )

        client = Client()
        client.force_login(self.user)

        response = client.get(
            f"/practice/sessions/{session.id}/progress/",
        )

        self.assertEqual(response.status_code, 404)


    def test_session_progress_view_requires_get(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/progress/",
        )

        self.assertEqual(response.status_code, 405)

    def test_complete_session_view(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/complete/",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["session_id"], session.id)
        self.assertEqual(
            data["status"],
            PracticeSession.Status.COMPLETED,
        )
        self.assertIsNotNone(data["completed_at"])


    def test_complete_session_view_requires_authentication(self):
        from django.test import Client

        client = Client()

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.post(
            f"/practice/sessions/{session.id}/complete/",
        )

        self.assertEqual(response.status_code, 401)


    def test_complete_session_view_rejects_other_users_session(self):
        from django.contrib.auth import get_user_model
        from django.test import Client

        User = get_user_model()

        other_user = User.objects.create_user(
            email="complete-other@test.com",
            password="testpass123",
            full_name="Complete Other User",
        )

        session = PracticeSession.objects.create(
            user=other_user,
            topic=self.topic,
        )

        client = Client()
        client.force_login(self.user)

        response = client.post(
            f"/practice/sessions/{session.id}/complete/",
        )

        self.assertEqual(response.status_code, 404)


    def test_complete_session_view_requires_post(self):
        from django.test import Client

        client = Client()
        client.force_login(self.user)

        session = PracticeSession.objects.create(
            user=self.user,
            topic=self.topic,
        )

        response = client.get(
            f"/practice/sessions/{session.id}/complete/",
        )

        self.assertEqual(response.status_code, 405)

    def test_get_next_question_filters_by_difficulty(self):
        from .services import create_practice_session, get_next_question

        hard_question = Question.objects.create(
            topic=self.topic,
            question="What is the hard test answer?",
            question_fingerprint="c" * 64,
            option_a="Hard A",
            option_b="Hard B",
            option_c="Hard C",
            option_d="Hard D",
            correct_answer="Hard A",
            explanation="Hard explanation.",
            difficulty="Hard",
            source="practice_test",
        )

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        next_question = get_next_question(
            session=session,
            difficulty="Hard",
        )

        self.assertEqual(next_question, hard_question)


    def test_get_next_question_returns_none_for_unavailable_difficulty(self):
        from .services import create_practice_session, get_next_question

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        self.assertIsNone(
            get_next_question(
                session=session,
                difficulty="Hard",
            )
        )


    def test_get_next_question_rejects_invalid_difficulty(self):
        from .services import create_practice_session, get_next_question

        session = create_practice_session(
            user=self.user,
            topic=self.topic,
        )

        with self.assertRaises(ValueError):
            get_next_question(
                session=session,
                difficulty="Invalid",
            )