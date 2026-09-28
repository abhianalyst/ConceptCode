from django.urls import path

from .views import (
    # Existing Practice views
    analytics_view,
    bookmark_status,
    chapters_view,
    complete_session,
    create_session,
    next_question,
    practice_results,
    practice_session,
    report_question,
    session_progress,
    start_practice_for_topic,
    student_dashboard,
    submit_session_answer,
    subjects_view,
    toggle_bookmark,
    topics_view,

    # Mock Test views
    mock_test_dashboard,
    mock_test_start,
    mock_test_session,
    mock_test_submit_answer,
    mock_test_toggle_review,
    mock_test_complete,
    mock_test_results,
    mock_test_history,
)


urlpatterns = [

    # ============================================================
    # STUDENT DASHBOARD
    # ============================================================

    path(
        "dashboard/",
        student_dashboard,
        name="student-dashboard",
    ),


    # ============================================================
    # ANALYTICS
    # ============================================================

    path(
        "analytics/",
        analytics_view,
        name="analytics",
    ),


    # ============================================================
    # PRACTICE SELECTION
    # ============================================================

    path(
        "subjects/",
        subjects_view,
        name="subjects",
    ),

    path(
        "subjects/<int:subject_id>/chapters/",
        chapters_view,
        name="chapters",
    ),

    path(
        "subjects/<int:subject_id>/chapters/<int:chapter_id>/topics/",
        topics_view,
        name="topics",
    ),


    # ============================================================
    # PRACTICE SESSION
    # ============================================================

    path(
        "topics/<int:topic_id>/sessions/",
        create_session,
        name="create-practice-session",
    ),

    path(
        "sessions/<int:session_id>/",
        practice_session,
        name="practice-session",
    ),

    path(
        "sessions/<int:session_id>/results/",
        practice_results,
        name="practice-results",
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


    # ============================================================
    # QUESTION BOOKMARK
    # ============================================================

    path(
        "questions/<int:question_id>/bookmark/",
        toggle_bookmark,
        name="toggle-bookmark",
    ),

    path(
        "questions/<int:question_id>/bookmark-status/",
        bookmark_status,
        name="bookmark-status",
    ),


    # ============================================================
    # QUESTION REPORT
    # ============================================================

    path(
        "questions/<int:question_id>/report/",
        report_question,
        name="report-question",
    ),


    # ============================================================
    # MOCK TEST
    # ============================================================

    # Mock Test Dashboard
    path(
        "mock-tests/",
        mock_test_dashboard,
        name="mock-test-dashboard",
    ),

    # Start a Mock Test
    path(
        "mock-tests/<int:test_id>/start/",
        mock_test_start,
        name="mock-test-start",
    ),

    # Mock Test Attempt / Session
    path(
        "mock-tests/attempt/<int:attempt_id>/",
        mock_test_session,
        name="mock-test-session",
    ),

    # Submit Mock Test Answer
    path(
        "mock-tests/attempt/<int:attempt_id>/answer/",
        mock_test_submit_answer,
        name="mock-test-submit-answer",
    ),

    # Toggle Review / Flag
    path(
        "mock-tests/attempt/<int:attempt_id>/toggle-review/",
        mock_test_toggle_review,
        name="mock-test-toggle-review",
    ),

    # Complete Mock Test
    path(
        "mock-tests/attempt/<int:attempt_id>/complete/",
        mock_test_complete,
        name="mock-test-complete",
    ),

    # Mock Test Results
    path(
        "mock-tests/attempt/<int:attempt_id>/results/",
        mock_test_results,
        name="mock-test-results",
    ),

    # Mock Test History
    path(
        "mock-tests/history/",
        mock_test_history,
        name="mock-test-history",
    ),

    path(
        "topics/<int:topic_id>/start/",
        start_practice_for_topic,
        name="start-practice-for-topic",
    ),

    path(
        "topics/<int:topic_id>/start/",
        start_practice_for_topic,
        name="start-practice-for-topic",
    ),
]