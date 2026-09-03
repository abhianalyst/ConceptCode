import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from apps.core.models import Question, Topic

from .models import PracticeSession
from .services import (
    complete_practice_session,
    create_practice_session,
    get_next_question,
    submit_answer,
)
from .progress import get_practice_progress

@require_POST
def create_session(request, topic_id):
    """Create a practice session for the requested topic."""

    topic = Topic.objects.filter(
        id=topic_id,
        is_active=True,
    ).first()

    if topic is None:
        return JsonResponse(
            {"error": "topic not found"},
            status=404,
        )

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "authentication required"},
            status=401,
        )

    session = create_practice_session(
        user=request.user,
        topic=topic,
    )

    return JsonResponse(
        {
            "session_id": session.id,
            "topic_id": topic.id,
            "status": session.status,
        },
        status=201,
    )


@require_GET
def next_question(request, session_id):
    """Return the next unanswered question for a practice session."""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "authentication required"},
            status=401,
        )

    session = PracticeSession.objects.filter(
        id=session_id,
        user=request.user,
    ).first()

    if session is None:
        return JsonResponse(
            {"error": "session not found"},
            status=404,
        )

    question = get_next_question(session=session)

    if question is None:
        return JsonResponse(
            {"message": "no questions remaining"},
            status=200,
        )

    return JsonResponse(
        {
            "question_id": question.id,
            "question": question.question,
            "options": [
                question.option_a,
                question.option_b,
                question.option_c,
                question.option_d,
            ],
            "difficulty": question.difficulty,
        },
        status=200,
    )


@require_POST
def submit_session_answer(request, session_id):
    """Submit and evaluate an answer for a practice session."""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "authentication required"},
            status=401,
        )

    session = PracticeSession.objects.filter(
        id=session_id,
        user=request.user,
    ).first()

    if session is None:
        return JsonResponse(
            {"error": "session not found"},
            status=404,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse(
            {"error": "invalid JSON"},
            status=400,
        )

    question_id = data.get("question_id")
    selected_answer = data.get("selected_answer")

    if question_id is None:
        return JsonResponse(
            {"error": "question_id is required"},
            status=400,
        )

    if selected_answer is None:
        return JsonResponse(
            {"error": "selected_answer is required"},
            status=400,
        )

    question = Question.objects.filter(
        id=question_id,
        is_active=True,
    ).first()

    if question is None:
        return JsonResponse(
            {"error": "question not found"},
            status=404,
        )

    try:
        attempt = submit_answer(
            session=session,
            question=question,
            selected_answer=selected_answer,
        )
    except ValueError as exc:
        return JsonResponse(
            {"error": str(exc)},
            status=400,
        )

    return JsonResponse(
        {
            "attempt_id": attempt.id,
            "question_id": question.id,
            "selected_answer": attempt.selected_answer,
            "is_correct": attempt.is_correct,
        },
        status=201,
    )

@require_GET
def session_progress(request, session_id):
    """Return progress statistics for a practice session."""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "authentication required"},
            status=401,
        )

    session = PracticeSession.objects.filter(
        id=session_id,
        user=request.user,
    ).first()

    if session is None:
        return JsonResponse(
            {"error": "session not found"},
            status=404,
        )

    progress = get_practice_progress(session=session)

    return JsonResponse(
        progress,
        status=200,
    )

@require_POST
def complete_session(request, session_id):
    """Complete a practice session."""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "authentication required"},
            status=401,
        )

    session = PracticeSession.objects.filter(
        id=session_id,
        user=request.user,
    ).first()

    if session is None:
        return JsonResponse(
            {"error": "session not found"},
            status=404,
        )

    session = complete_practice_session(session=session)

    return JsonResponse(
        {
            "session_id": session.id,
            "status": session.status,
            "completed_at": session.completed_at.isoformat()
            if session.completed_at
            else None,
        },
        status=200,
    )