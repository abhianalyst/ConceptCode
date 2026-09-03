from django.urls import path

from .views import (
    complete_session,
    create_session,
    next_question,
    session_progress,
    submit_session_answer,
)


urlpatterns = [
    path(
        "topics/<int:topic_id>/sessions/",
        create_session,
        name="create-practice-session",
    ),
    path(
        "sessions/<int:session_id>/next/",
        next_question,
        name="practice-next-question",
    ),
    path(
        "sessions/<int:session_id>/answer/",
        submit_session_answer,
        name="practice-submit-answer",
    ),
    path(
        "sessions/<int:session_id>/progress/",
        session_progress,
        name="practice-session-progress",
    ),
    path(
        "sessions/<int:session_id>/complete/",
        complete_session,
        name="practice-complete-session",
    ),
]
