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

    answered_question_ids = session.attempts.values_list(
        "question_id",
        flat=True,
    )

    questions = (
        session.topic.questions
        .filter(is_active=True)
        .exclude(id__in=answered_question_ids)
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
    )
    

@transaction.atomic
def complete_practice_session(*, session) -> PracticeSession:
    """Mark a practice session as completed."""

    if session is None:
        raise ValueError("session is required")

    if session.status == PracticeSession.Status.COMPLETED:
        return session

    from django.utils import timezone

    session.status = PracticeSession.Status.COMPLETED
    session.completed_at = timezone.now()
    session.save(
        update_fields=["status", "completed_at"],
    )

    return session


