from apps.core.models import Question

from .models import PracticeSession


def get_practice_progress(*, session) -> dict:
    """Return progress statistics for a practice session."""

    if session is None:
        raise ValueError("session is required")

    total_questions = (
        Question.objects
        .filter(topic=session.topic, is_active=True)
        .count()
    )

    answered_questions = session.attempts.count()

    correct_answers = session.attempts.filter(
        is_correct=True,
    ).count()

    incorrect_answers = session.attempts.filter(
        is_correct=False,
    ).count()

    percentage = (
        (answered_questions / total_questions) * 100
        if total_questions
        else 0
    )

    return {
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "remaining_questions": max(
            total_questions - answered_questions,
            0,
        ),
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "percentage": percentage,
    }
