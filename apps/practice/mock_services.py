# apps/practice/services.py

from django.db import transaction
from django.utils import timezone

from .models import PracticeAttempt, PracticeSession


@transaction.atomic
def create_practice_session(*, user, topic) -> PracticeSession:
    """Create a new active practice session for a user and topic."""

    if user is None:
        raise ValueError("user is required")

    if topic is None:
        raise ValueError("topic is required")

    return PracticeSession.objects.create(
        user=user,
        topic=topic,
    )
    

def get_next_question(*, session, difficulty=None):
    """Return the next unanswered active question for a practice session."""
    
    if session is None:
        raise ValueError("session is required")

    if difficulty is not None and difficulty not in (
        "Easy",
        "Medium",
        "Hard",
    ):
        raise ValueError("invalid difficulty")

    from django.utils import timezone
    from datetime import timedelta
    
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    recently_correct = session.attempts.filter(
        is_correct=True,
        answered_at__gte=seven_days_ago
    ).values_list('question_id', flat=True)
    
    answered_question_ids = session.attempts.values_list(
        "question_id",
        flat=True,
    )

    questions = (
        session.topic.questions
        .filter(is_active=True)
        .exclude(id__in=answered_question_ids)
        .exclude(id__in=recently_correct)
    )

    if difficulty is not None:
        questions = questions.filter(
            difficulty=difficulty,
        )

    return questions.order_by(
        "created_at",
        "id",
    ).first()


@transaction.atomic
def submit_answer(
    *,
    session,
    question,
    selected_answer,
    time_taken=0.0,
) -> PracticeAttempt:
    """Record a student's answer and evaluate correctness."""

    if session is None:
        raise ValueError("session is required")

    if question is None:
        raise ValueError("question is required")

    if not isinstance(selected_answer, str) or not selected_answer.strip():
        raise ValueError("selected_answer is required")

    if question.topic_id != session.topic_id:
        raise ValueError("question does not belong to session topic")

    if session.attempts.filter(question=question).exists():
        raise ValueError("question has already been answered")

    selected_answer = selected_answer.strip()

    is_correct = selected_answer == question.correct_answer

    return PracticeAttempt.objects.create(
        session=session,
        question=question,
        selected_answer=selected_answer,
        is_correct=is_correct,
        time_taken=time_taken,
    )
    

@transaction.atomic
def complete_practice_session(*, session) -> PracticeSession:
    """Mark a practice session as completed."""

    if session is None:
        raise ValueError("session is required")

    if session.status == PracticeSession.Status.COMPLETED:
        return session

    session.status = PracticeSession.Status.COMPLETED
    session.completed_at = timezone.now()
    session.save(
        update_fields=["status", "completed_at"],
    )

    return session


# ============================================================
# MOCK TEST SERVICE
# ============================================================

class MockTestService:
    """Service for creating and managing mock tests."""
    
    CORRECT_MARKS = 4
    INCORRECT_MARKS = -1
    
    @staticmethod
    def start_attempt(user, mock_test_id):
        """Start a mock test attempt."""
        from apps.core.models import MockTest, MockTestAttempt
        
        mock_test = MockTest.objects.get(id=mock_test_id, is_active=True)
        existing = MockTestAttempt.objects.filter(
            user=user,
            mock_test=mock_test,
            status=MockTestAttempt.Status.IN_PROGRESS
        ).first()
        
        if existing:
            return existing
        
        return MockTestAttempt.objects.create(
            user=user,
            mock_test=mock_test,
            status=MockTestAttempt.Status.IN_PROGRESS
        )
    
    @staticmethod
    def submit_answer(attempt, question_id, selected_answer, time_spent=0):
        """Submit an answer for a mock test question."""
        from apps.core.models import Question, MockTestAnswer
        
        question = Question.objects.get(id=question_id)
        
        existing = MockTestAnswer.objects.filter(
            attempt=attempt,
            question=question
        ).first()
        
        if existing:
            existing.selected_answer = selected_answer
            existing.is_correct = selected_answer == question.correct_answer
            existing.time_spent = time_spent
            existing.answered_at = timezone.now()
            existing.save()
            return existing
        
        return MockTestAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            is_correct=selected_answer == question.correct_answer,
            time_spent=time_spent
        )
    
    @staticmethod
    def toggle_review(attempt, question_id):
        """Toggle review status for a question."""
        from apps.core.models import MockTestAnswer
        
        answer = MockTestAnswer.objects.filter(
            attempt=attempt,
            question_id=question_id
        ).first()
        
        if answer:
            answer.is_marked_for_review = not answer.is_marked_for_review
            answer.save()
            return answer.is_marked_for_review
        
        answer = MockTestAnswer.objects.create(
            attempt=attempt,
            question_id=question_id,
            selected_answer='',
            is_correct=False,
            is_marked_for_review=True
        )
        return True
    
    @staticmethod
    def calculate_score(attempt):
        """Calculate score for a mock test attempt."""
        answers = attempt.answers.all()
        total_questions = attempt.mock_test.total_questions
        
        correct = 0
        incorrect = 0
        
        for answer in answers:
            if answer.selected_answer and answer.selected_answer != '':
                if answer.is_correct:
                    correct += 1
                else:
                    incorrect += 1
        
        # Calculate unattempted
        answered_count = answers.filter(selected_answer__isnull=False).exclude(selected_answer='').count()
        unattempted = total_questions - answered_count
        
        # Calculate score: +4 for correct, -1 for incorrect
        score = (correct * 4) + (incorrect * -1)
        
        return {
            'score': score,
            'correct': correct,
            'incorrect': incorrect,
            'unattempted': unattempted,
            'total': total_questions,
            'percentage': round((correct / total_questions) * 100, 1) if total_questions > 0 else 0
        }
    
    @staticmethod
    def complete_attempt(attempt):
        """Complete a mock test attempt."""
        from apps.core.models import MockTestAttempt
        
        if attempt.status == MockTestAttempt.Status.COMPLETED:
            return attempt
        
        result = MockTestService.calculate_score(attempt)
        
        attempt.status = MockTestAttempt.Status.COMPLETED
        attempt.completed_at = timezone.now()
        attempt.score = result['score']
        attempt.correct_count = result['correct']
        attempt.incorrect_count = result['incorrect']
        attempt.unattempted_count = result['unattempted']
        attempt.save()
        
        return attempt
    
    @staticmethod
    def auto_submit_expired():
        """Auto-submit expired mock tests."""
        from apps.core.models import MockTestAttempt
        
        expired = MockTestAttempt.objects.filter(
            status=MockTestAttempt.Status.IN_PROGRESS,
            started_at__lt=timezone.now() - timedelta(minutes=200)
        )
        
        for attempt in expired:
            MockTestService.complete_attempt(attempt)
            attempt.status = MockTestAttempt.Status.AUTO_SUBMITTED
            attempt.save()