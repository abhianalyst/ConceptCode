# apps/practice/views.py

import json
import logging
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import models, IntegrityError
from django.urls import reverse

from apps.core.models import Subject, Chapter, Topic, Question, MockTest, MockTestAttempt, MockTestQuestion, MockTestAnswer, Bookmark, QuestionReport

from .models import PracticeSession, PracticeAttempt

from .services import (
    complete_practice_session,
    create_practice_session,
    get_next_question,
    submit_answer,
    MockTestService,
)

from .progress import get_practice_progress
from .dashboard import get_student_dashboard

logger = logging.getLogger(__name__)


# ============================================================
# PRACTICE SESSION VIEWS
# ============================================================

@require_POST
def create_session(request, topic_id):
    """Create a practice session for the requested topic."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "authentication required"}, status=401)

    topic = get_object_or_404(Topic, id=topic_id, is_active=True)
    questions = Question.objects.filter(topic=topic, is_active=True)

    if not questions.exists():
        return JsonResponse({"error": "No questions available for this topic yet."}, status=404)

    session = create_practice_session(user=request.user, topic=topic)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "session_id": session.id,
            "topic_id": topic.id,
            "status": session.status,
        }, status=201)

    return redirect("practice:practice-session", session_id=session.id)


@login_required
def practice_session(request, session_id):
    """Render the practice session page."""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
    question = get_next_question(session=session)
    total_questions = Question.objects.filter(topic=session.topic, is_active=True).count()

    context = {
        "session": session,
        "question": question,
        "total_questions": total_questions,
    }

    return render(request, "practice/practice.html", context)


@login_required
def practice_results(request, session_id):
    """Display practice session results."""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)

    attempts = session.attempts.all()
    total_questions = session.topic.questions.filter(is_active=True).count()
    answered_questions = attempts.count()
    correct_answers = attempts.filter(is_correct=True).count()
    incorrect_answers = attempts.filter(is_correct=False).count()
    skipped_questions = max(total_questions - answered_questions, 0)

    accuracy = round((correct_answers / total_questions) * 100, 0) if total_questions > 0 else 0

    total_time_spent = sum(attempt.time_taken for attempt in attempts)
    minutes = int(total_time_spent // 60)
    seconds = int(total_time_spent % 60)
    time_display = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

    previous_session = (
        PracticeSession.objects
        .filter(user=request.user, topic=session.topic, status=PracticeSession.Status.COMPLETED)
        .exclude(id=session.id)
        .order_by("-completed_at")
        .first()
    )

    previous_accuracy = 0
    if previous_session:
        previous_attempts = previous_session.attempts.all()
        previous_total = previous_session.topic.questions.filter(is_active=True).count()
        previous_correct = previous_attempts.filter(is_correct=True).count()
        previous_accuracy = round((previous_correct / previous_total) * 100, 0) if previous_total > 0 else 0

    weak_areas = []
    if incorrect_answers > 0:
        weak_areas.append({
            "name": session.topic.chapter.name,
            "incorrect": incorrect_answers,
            "skipped": skipped_questions,
        })

    context = {
        "session": session,
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "skipped_questions": skipped_questions,
        "accuracy": accuracy,
        "previous_accuracy": previous_accuracy,
        "weak_areas": weak_areas,
        "topic": session.topic,
        "time_display": time_display,
    }

    return render(request, "practice/results.html", context)


@require_GET
@login_required
def next_question(request, session_id):
    """Return the next unanswered question for a practice session."""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
    question = get_next_question(session=session)

    if question is None:
        return JsonResponse({"completed": True, "message": "Practice session completed!"})

    return JsonResponse({
        "question_id": question.id,
        "question_text": question.question,
        "options": {
            "A": question.option_a,
            "B": question.option_b,
            "C": question.option_c,
            "D": question.option_d,
        },
        "question_number": session.attempts.count() + 1,
        "difficulty": question.difficulty,
    })


@csrf_exempt
@require_POST
@login_required
def submit_session_answer(request, session_id):
    """Submit an answer for a practice session question."""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)

    try:
        data = json.loads(request.body)
        question_id = data.get("question_id")
        selected_answer = data.get("selected_answer", "").upper()
        time_taken = data.get("time_taken", 0.0)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    if not question_id:
        return JsonResponse({"error": "question_id is required"}, status=400)

    question = get_object_or_404(Question, id=question_id, is_active=True)

    if question.topic_id != session.topic_id:
        return JsonResponse({"error": "Question does not belong to this session's topic"}, status=400)

    if session.attempts.filter(question=question).exists():
        return JsonResponse({"error": "Question has already been answered"}, status=400)

    attempt = submit_answer(
        session=session,
        question=question,
        selected_answer=selected_answer,
        time_taken=time_taken,
    )

    return JsonResponse({
        "is_correct": attempt.is_correct,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "question_number": session.attempts.count(),
        "difficulty": question.difficulty,
    })


@require_POST
@login_required
def complete_session(request, session_id):
    """Complete a practice session."""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
    complete_practice_session(session=session)

    return JsonResponse({
        "success": True,
        "message": "Practice session completed!",
        "session_id": session.id,
    })


@require_GET
@login_required
def session_progress(request, session_id):
    """Get progress for a practice session."""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
    progress = get_practice_progress(session=session)
    return JsonResponse(progress)


@login_required
def student_dashboard(request):
    """Student dashboard showing practice history and stats."""
    from apps.core.models import MockTestAttempt, MockTest
    from apps.ml_module.services import WeakAreaDetector

    dashboard_data = get_student_dashboard(user=request.user)

    mock_attempts = MockTestAttempt.objects.filter(
        user=request.user,
        status__in=[MockTestAttempt.Status.COMPLETED, MockTestAttempt.Status.AUTO_SUBMITTED]
    )
    total_mock_attempts = mock_attempts.count()
    avg_mock_score_data = mock_attempts.aggregate(avg_score=models.Avg('score'))
    avg_mock_score = avg_mock_score_data.get('avg_score', 0) or 0

    upcoming_mock_tests = MockTest.objects.filter(
        is_active=True,
        scheduled_date__isnull=False
    ).order_by('scheduled_date')[:3]

    # ML Predictions
    weak_areas = WeakAreaDetector.get_weak_topics(request.user, limit=3)
    recommended_topic = WeakAreaDetector.get_recommended_topic(request.user)

    context = {
        'total_sessions': dashboard_data.get('total_sessions', 0),
        'completed_sessions': dashboard_data.get('completed_sessions', 0),
        'active_sessions': dashboard_data.get('active_sessions', 0),
        'total_attempts': dashboard_data.get('total_attempts', 0),
        'correct_answers': dashboard_data.get('correct_answers', 0),
        'incorrect_answers': dashboard_data.get('incorrect_answers', 0),
        'accuracy': dashboard_data.get('accuracy', 0),
        'recent_sessions': dashboard_data.get('recent_sessions', []),
        'topic_performance': dashboard_data.get('topic_performance', []),
        'active_session': dashboard_data.get('active_session', None),
        'streak_days': dashboard_data.get('streak_days', 0),
        'today_attempts': dashboard_data.get('today_attempts', 0),
        'study_time': dashboard_data.get('study_time', '0m'),
        'user_rank': dashboard_data.get('user_rank', 1),
        'subject_performance': dashboard_data.get('subject_performance', []),
        'upcoming_mock_tests': upcoming_mock_tests,
        'recent_performance': dashboard_data.get('recent_performance', []),
        'xp_earned': dashboard_data.get('xp_earned', 0),
        'xp_goal': dashboard_data.get('xp_goal', 200),
        'xp_progress': dashboard_data.get('xp_progress', 0),
        'completed_goals': dashboard_data.get('completed_goals', 0),
        'total_goals': dashboard_data.get('total_goals', 3),
        'total_mock_attempts': total_mock_attempts,
        'avg_mock_score': round(avg_mock_score, 1),
        'weak_areas': weak_areas,
        'recommended_topic': recommended_topic,
    }

    return render(request, "practice/student_dashboard.html", context)


# ============================================================
# PRACTICE SELECTION VIEWS
# ============================================================

@login_required
def subjects_view(request):
    """View all subjects for practice selection with progress."""
    subjects = Subject.objects.filter(is_active=True).prefetch_related("chapters__topics")

    subject_data = []
    for subject in subjects:
        topics = Topic.objects.filter(chapter__subject=subject, is_active=True)
        total_questions = sum(topic.questions.filter(is_active=True).count() for topic in topics)
        attempted_questions = (
            PracticeAttempt.objects
            .filter(session__user=request.user, session__topic__in=topics)
            .values("question")
            .distinct()
            .count()
        )

        progress = min(round((attempted_questions / total_questions) * 100), 100) if total_questions > 0 else 0

        if progress >= 100:
            status = "completed"
        elif progress > 0:
            status = "in-progress"
        else:
            status = "not-started"

        subject_data.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "progress": progress,
            "status": status,
            "chapters": subject.chapters.filter(is_active=True),
        })

    return render(request, "practice/subjects.html", {"subjects": subject_data})


@login_required
def chapters_view(request, subject_id):
    """View all chapters for a specific subject."""
    subject = get_object_or_404(Subject, id=subject_id, is_active=True)
    chapters = subject.chapters.filter(is_active=True).prefetch_related("topics")

    return render(request, "practice/chapters.html", {
        "subject": subject,
        "chapters": chapters,
    })


@login_required
def topics_view(request, subject_id, chapter_id):
    """View all topics for a specific chapter with completion data."""
    subject = get_object_or_404(Subject, id=subject_id, is_active=True)
    chapter = get_object_or_404(Chapter, id=chapter_id, is_active=True, subject=subject)
    topics = chapter.topics.filter(is_active=True).order_by('name')

    attempts = PracticeAttempt.objects.filter(session__user=request.user)

    topics_data = []
    for topic in topics:
        total_questions = topic.questions.filter(is_active=True).count()
        topic_attempts = attempts.filter(session__topic=topic)
        attempted_questions = topic_attempts.values('question').distinct().count()
        completion = min(round((attempted_questions / total_questions) * 100), 100) if total_questions > 0 else 0
        total_attempted = topic_attempts.count()
        correct_attempts = topic_attempts.filter(is_correct=True).count()
        accuracy = round((correct_attempts / total_attempted) * 100, 1) if total_attempted > 0 else 0

        if total_attempted >= 3 and accuracy < 60:
            status = 'needs_attention'
        elif completion == 100 and accuracy >= 60:
            status = 'completed'
        elif completion > 0:
            status = 'in_progress'
        else:
            status = 'not_started'

        topics_data.append({
            'id': topic.id,
            'name': topic.name,
            'total_questions': total_questions,
            'completion': completion,
            'accuracy': accuracy,
            'status': status,
            'attempted_count': attempted_questions,
            'total_attempted': total_attempted,
            'correct_attempts': correct_attempts,
        })

    return render(request, 'practice/topics.html', {
        'subject': subject,
        'chapter': chapter,
        'topics_data': topics_data,
    })


# ============================================================
# ANALYTICS VIEW
# ============================================================

@login_required
def analytics_view(request):
    """Learning Analytics page with performance insights."""
    from django.db.models import Avg
    from datetime import datetime, timedelta
    from apps.core.models import Subject, Topic
    from apps.ml_module.services import WeakAreaDetector

    attempts = PracticeAttempt.objects.filter(session__user=request.user)
    sessions = PracticeSession.objects.filter(user=request.user)

    total_attempts = attempts.count()
    correct_attempts = attempts.filter(is_correct=True).count()
    accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts > 0 else 0

    completed_sessions = sessions.filter(status=PracticeSession.Status.COMPLETED).count()
    total_sessions = sessions.count()
    completion_rate = round((completed_sessions / total_sessions) * 100, 1) if total_sessions > 0 else 0

    streak_days = 5
    avg_time_per_question = 2
    total_study_time = total_attempts * avg_time_per_question
    total_hours = total_study_time // 60
    total_minutes = total_study_time % 60
    total_study_time_display = f"{total_hours}h {total_minutes}m"

    weekly_trend = []
    now = datetime.now().date()
    colors = ['#4facfe', '#6c8cff', '#a8c8ff', '#c5dfff']
    for i in range(3, -1, -1):
        week_start = now - timedelta(days=7 * (i + 1))
        week_end = now - timedelta(days=7 * i)
        week_attempts = attempts.filter(
            answered_at__date__gte=week_start,
            answered_at__date__lt=week_end
        ).count()
        value = min(round((week_attempts / 10) * 100), 100) if total_attempts > 0 else 0
        weekly_trend.append({
            'label': f'Week {4 - i}',
            'value': value,
            'color': colors[i]
        })

    subject_progress = []
    subjects = Subject.objects.filter(is_active=True)
    for subject in subjects:
        topics = Topic.objects.filter(chapter__subject=subject, is_active=True)
        total_topics = topics.count()
        completed_topics = 0
        for topic in topics:
            topic_questions = topic.questions.filter(is_active=True).count()
            user_attempts = attempts.filter(session__topic=topic).values('question').distinct().count()
            if topic_questions > 0 and user_attempts >= topic_questions:
                completed_topics += 1
        progress = round((completed_topics / total_topics) * 100) if total_topics > 0 else 0
        subject_progress.append({
            'name': subject.name,
            'progress': progress,
            'completed': completed_topics,
            'total': total_topics,
            'color': '#4facfe' if progress >= 70 else '#ffc107' if progress >= 40 else '#dc3545'
        })

    topic_accuracy = []
    topics_with_attempts = Topic.objects.filter(
        questions__practice_attempts__session__user=request.user
    ).distinct()
    for topic in topics_with_attempts[:5]:
        topic_attempts = attempts.filter(session__topic=topic)
        total = topic_attempts.count()
        correct = topic_attempts.filter(is_correct=True).count()
        acc = round((correct / total) * 100, 1) if total > 0 else 0
        topic_accuracy.append({
            'name': topic.name[:20],
            'accuracy': acc
        })

    daily_activity = []
    for i in range(6, -1, -1):
        date = now - timedelta(days=i)
        day_attempts = attempts.filter(answered_at__date=date).count()
        activity_level = min(day_attempts, 5) if day_attempts > 0 else 0
        daily_activity.append({
            'date': date.strftime('%b %d'),
            'day': date.strftime('%a')[0],
            'activity': day_attempts,
            'activity_level': activity_level
        })

    # ML Predictions
    weak_areas = WeakAreaDetector.get_weak_topics(request.user, limit=5)
    recommended_topic = WeakAreaDetector.get_recommended_topic(request.user)

    context = {
        'total_study_time': total_study_time_display,
        'accuracy': accuracy,
        'completion_rate': completion_rate,
        'streak_days': streak_days,
        'weekly_trend': weekly_trend,
        'subject_progress': subject_progress,
        'topic_accuracy': topic_accuracy,
        'daily_activity': daily_activity,
        'weak_areas': weak_areas,
        'recommended_topic': recommended_topic,
    }

    return render(request, 'practice/analytics.html', context)


# ============================================================
# BOOKMARK & REPORT (RESTORED)
# ============================================================

@login_required
@require_POST
def toggle_bookmark(request, question_id):
    """Toggle bookmark for a question."""
    question = get_object_or_404(Question, id=question_id, is_active=True)

    bookmark = Bookmark.objects.filter(user=request.user, question=question)

    if bookmark.exists():
        bookmark.delete()
        return JsonResponse({'bookmarked': False, 'message': 'Bookmark removed'})
    else:
        Bookmark.objects.create(user=request.user, question=question)
        return JsonResponse({'bookmarked': True, 'message': 'Bookmark added'})


@login_required
@require_GET
def bookmark_status(request, question_id):
    """Check if a question is bookmarked."""
    question = get_object_or_404(Question, id=question_id, is_active=True)
    bookmarked = Bookmark.objects.filter(user=request.user, question=question).exists()
    return JsonResponse({'bookmarked': bookmarked})


@login_required
@require_POST
def report_question(request, question_id):
    """Report a question as incorrect or unclear."""
    question = get_object_or_404(Question, id=question_id, is_active=True)

    try:
        data = json.loads(request.body)
        report_type = data.get('report_type', 'other')
        description = data.get('description', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not description:
        return JsonResponse({'error': 'Description is required'}, status=400)

    report_type_map = {
        'wrong_answer': QuestionReport.ReportType.WRONG_ANSWER,
        'incorrect_explanation': QuestionReport.ReportType.INCORRECT_EXPLANATION,
        'typo': QuestionReport.ReportType.TYPO,
        'duplicate': QuestionReport.ReportType.DUPLICATE,
        'other': QuestionReport.ReportType.OTHER,
    }

    report = QuestionReport.objects.create(
        question=question,
        reported_by=request.user,
        report_type=report_type_map.get(report_type, QuestionReport.ReportType.OTHER),
        description=description,
        status=QuestionReport.ReportStatus.PENDING
    )

    return JsonResponse({
        'success': True,
        'message': 'Question reported successfully. Our team will review it.',
        'report_id': report.id
    })


# ============================================================
# MOCK TEST VIEWS
# ============================================================

@login_required
def mock_test_dashboard(request):
    """Display available mock tests and past attempts."""
    available_tests = MockTest.objects.filter(is_active=True)

    past_attempts = MockTestAttempt.objects.filter(
        user=request.user
    ).select_related('mock_test').order_by('-started_at')[:10]

    total_attempts = MockTestAttempt.objects.filter(user=request.user).count()

    avg_score_data = MockTestAttempt.objects.filter(
        user=request.user,
        status__in=[MockTestAttempt.Status.COMPLETED, MockTestAttempt.Status.AUTO_SUBMITTED]
    ).aggregate(avg_score=models.Avg('score'))

    avg_score = avg_score_data.get('avg_score', 0) or 0

    context = {
        'available_tests': available_tests,
        'past_attempts': past_attempts,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 1),
    }

    return render(request, 'practice/mock_test_dashboard.html', context)


@login_required
def mock_test_start(request, test_id):
    """Start a mock test."""
    mock_test = get_object_or_404(MockTest, id=test_id, is_active=True)

    existing = MockTestAttempt.objects.filter(
        user=request.user,
        mock_test=mock_test,
        status=MockTestAttempt.Status.IN_PROGRESS
    ).first()

    if existing:
        return redirect('practice:mock-test-session', attempt_id=existing.id)

    attempt = MockTestService.start_attempt(request.user, test_id)
    return redirect('practice:mock-test-session', attempt_id=attempt.id)


@login_required
def mock_test_session(request, attempt_id):
    """Render the mock test session."""
    from django.utils import timezone
    from datetime import timedelta

    attempt = get_object_or_404(MockTestAttempt, id=attempt_id, user=request.user)

    if attempt.status != MockTestAttempt.Status.IN_PROGRESS:
        return redirect('practice:mock-test-results', attempt_id=attempt.id)

    if timezone.now() > attempt.started_at + timedelta(minutes=attempt.mock_test.duration_minutes):
        MockTestService.complete_attempt(attempt)
        return redirect('practice:mock-test-results', attempt_id=attempt.id)

    mock_questions = MockTestQuestion.objects.filter(
        mock_test=attempt.mock_test
    ).select_related('question').order_by('order')

    questions_data = []
    for mq in mock_questions:
        answer = MockTestAnswer.objects.filter(attempt=attempt, question=mq.question).first()
        questions_data.append({
            'order': mq.order,
            'question': mq.question,
            'answer': answer,
            'is_answered': answer is not None and answer.selected_answer != '',
            'is_reviewed': answer.is_marked_for_review if answer else False,
        })

    elapsed = (timezone.now() - attempt.started_at).total_seconds()
    total_seconds = attempt.mock_test.duration_minutes * 60
    remaining = max(0, total_seconds - elapsed)

    current_index = 0
    for idx, qd in enumerate(questions_data):
        if not qd['is_answered']:
            current_index = idx
            break

    context = {
        'attempt': attempt,
        'mock_test': attempt.mock_test,
        'questions_data': questions_data,
        'current_index': current_index,
        'remaining_time': remaining,
        'total_questions': len(questions_data),
    }

    return render(request, 'practice/mock_test.html', context)


@login_required
@require_POST
def mock_test_submit_answer(request, attempt_id):
    """Submit an answer for a mock test question."""
    attempt = get_object_or_404(MockTestAttempt, id=attempt_id, user=request.user)

    if attempt.status != MockTestAttempt.Status.IN_PROGRESS:
        return JsonResponse({'error': 'Test already completed'}, status=400)

    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer', '').upper()
        time_spent = data.get('time_spent', 0)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    answer = MockTestService.submit_answer(attempt, question_id, selected_answer, time_spent)

    return JsonResponse({
        'success': True,
        'is_correct': answer.is_correct,
        'correct_answer': answer.question.correct_answer,
        'explanation': answer.question.explanation,
    })


@login_required
@require_POST
def mock_test_toggle_review(request, attempt_id):
    """Toggle review status for a mock test question."""
    attempt = get_object_or_404(MockTestAttempt, id=attempt_id, user=request.user)

    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    is_reviewed = MockTestService.toggle_review(attempt, question_id)

    return JsonResponse({'success': True, 'is_reviewed': is_reviewed})


@login_required
@require_POST
def mock_test_complete(request, attempt_id):
    """Complete a mock test."""
    attempt = get_object_or_404(MockTestAttempt, id=attempt_id, user=request.user)

    if attempt.status != MockTestAttempt.Status.IN_PROGRESS:
        return JsonResponse({'error': 'Test already completed'}, status=400)

    MockTestService.complete_attempt(attempt)

    return JsonResponse({
        'success': True,
        'redirect_url': reverse('practice:mock-test-results', args=[attempt.id])
    })


@login_required
def mock_test_results(request, attempt_id):
    """Display mock test results."""
    attempt = get_object_or_404(MockTestAttempt, id=attempt_id, user=request.user)

    if attempt.status == MockTestAttempt.Status.IN_PROGRESS:
        return redirect('practice:mock-test-session', attempt_id=attempt.id)

    result = MockTestService.calculate_score(attempt)
    answers = attempt.answers.select_related('question').all()

    time_stats = {
        'total_time': sum(a.time_spent for a in answers),
        'avg_time_per_question': round(sum(a.time_spent for a in answers) / len(answers), 1) if answers else 0,
    }

    subject_breakdown = {}
    for answer in answers:
        subject_name = answer.question.topic.chapter.subject.name
        if subject_name not in subject_breakdown:
            subject_breakdown[subject_name] = {'correct': 0, 'incorrect': 0, 'total': 0}

        subject_breakdown[subject_name]['total'] += 1
        if answer.is_correct:
            subject_breakdown[subject_name]['correct'] += 1
        elif answer.selected_answer:
            subject_breakdown[subject_name]['incorrect'] += 1

    context = {
        'attempt': attempt,
        'mock_test': attempt.mock_test,
        'result': result,
        'answers': answers,
        'subject_breakdown': subject_breakdown,
        'time_stats': time_stats,
    }

    return render(request, 'practice/mock_test_results.html', context)


@login_required
def mock_test_history(request):
    """View all past mock test attempts."""
    attempts = MockTestAttempt.objects.filter(
        user=request.user
    ).select_related('mock_test').order_by('-started_at')

    context = {'attempts': attempts}

    return render(request, 'practice/mock_test_history.html', context)

@login_required
def start_practice_for_topic(request, topic_id):
    """
    GET-friendly wrapper that creates a practice session and redirects
    to the session page. Used by the Study Planner's 'Practice' button.
    """
    topic = get_object_or_404(Topic, id=topic_id, is_active=True)

    if not topic.questions.filter(is_active=True).exists():
        messages.error(request, "No questions available for this topic yet.")
        return redirect("practice:topics", subject_id=topic.chapter.subject.id, chapter_id=topic.chapter.id)

    session = create_practice_session(user=request.user, topic=topic)
    return redirect("practice:practice-session", session_id=session.id)