from django.db.models import Count, Q, Sum
from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Question, Subject, Topic

from .models import PracticeAttempt, PracticeSession


def get_student_dashboard(*, user) -> dict:
    """Return dashboard statistics and recent practice sessions."""
    if user is None:
        raise ValueError("user is required")

    # Get all sessions for this user
    sessions = PracticeSession.objects.filter(user=user)
    
    # Get all attempts for this user
    attempts = PracticeAttempt.objects.filter(session__user=user)

    # ===== BASIC STATS =====
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(
        status=PracticeSession.Status.COMPLETED,
    ).count()
    
    active_sessions = sessions.filter(
        status=PracticeSession.Status.ACTIVE,
    ).count()

    total_attempts = attempts.count()
    correct_answers = attempts.filter(is_correct=True).count()
    incorrect_answers = attempts.filter(is_correct=False).count()

    # Calculate accuracy
    accuracy = (
        round((correct_answers / total_attempts) * 100, 1)
        if total_attempts > 0
        else 0
    )

    # ===== FR-02-02: QUESTIONS ATTEMPTED TODAY =====
    today = timezone.now().date()
    today_start = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time())
    )
    today_attempts = attempts.filter(
        answered_at__gte=today_start
    ).count()

    # ===== FR-02-04: STUDY TIME THIS WEEK =====
    week_start = today - timedelta(days=7)
    week_start = timezone.make_aware(
        timezone.datetime.combine(week_start, timezone.datetime.min.time())
    )
    week_attempts = attempts.filter(
        answered_at__gte=week_start
    ).count()
    
    # Estimate study time (2 minutes per question average)
    avg_time_per_question = 2  # minutes
    study_time_minutes = week_attempts * avg_time_per_question
    study_time_hours = study_time_minutes // 60
    study_time_remaining_minutes = study_time_minutes % 60
    study_time_display = f"{study_time_hours}h {study_time_remaining_minutes}m" if study_time_hours > 0 else f"{study_time_minutes}m"

    # ===== FR-02-05: LEADERBOARD RANK (Simplified) =====
    # Get all users and their correct answers count
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Count users with more correct answers than current user
    user_correct = attempts.filter(is_correct=True).count()
    
    # Get all users with their correct answer counts
    all_users = User.objects.annotate(
        correct_count=Count('practice_sessions__attempts', filter=Q(practice_sessions__attempts__is_correct=True))
    )
    
    # Count users with more correct answers
    higher_users = all_users.filter(correct_count__gt=user_correct).count()
    user_rank = higher_users + 1

    # ===== FR-02-06: SUBJECT-WISE PERFORMANCE =====
    subject_performance = []
    subjects = Subject.objects.filter(is_active=True)
    
    for subject in subjects:
        # Get all topics in this subject
        topics = Topic.objects.filter(chapter__subject=subject, is_active=True)
        
        # Get attempts for this subject
        subject_attempts = attempts.filter(session__topic__in=topics)
        subject_total = subject_attempts.count()
        subject_correct = subject_attempts.filter(is_correct=True).count()
        subject_accuracy = round((subject_correct / subject_total) * 100, 1) if subject_total > 0 else 0
        
        # Color for chart
        color_map = {
            'Biology': '#28a745',  # Green
            'Chemistry': '#0d6efd',  # Blue
            'Physics': '#dc3545',  # Red
        }
        
        subject_performance.append({
            'name': subject.name,
            'accuracy': subject_accuracy,
            'color': color_map.get(subject.name, '#6c757d'),
        })

    # ===== FR-02-07: TOP 3 WEAKEST TOPICS =====
    # (Placeholder - will be enhanced by ML module later)
    weak_topics = []
    
    # Get topics with attempts and calculate accuracy
    topics_with_attempts = Topic.objects.filter(
        questions__practice_attempts__session__user=user
    ).distinct()
    
    topic_stats = []
    for topic in topics_with_attempts:
        topic_attempts = attempts.filter(session__topic=topic)
        total = topic_attempts.count()
        correct = topic_attempts.filter(is_correct=True).count()
        accuracy = round((correct / total) * 100, 1) if total > 0 else 0
        
        # Only include topics with at least 3 attempts
        if total >= 3:
            topic_stats.append({
                'name': topic.name,
                'accuracy': accuracy,
                'total': total,
                'correct': correct,
            })
    
    # Sort by accuracy (lowest first) and get top 3
    topic_stats.sort(key=lambda x: x['accuracy'])
    weak_topics = topic_stats[:3]

    # ===== FR-02-08: CONTINUE WHERE YOU LEFT OFF =====
    # Get active session for resume
    active_session = sessions.filter(status=PracticeSession.Status.ACTIVE).first()
    active_session_data = None
    
    if active_session:
        answered_questions = active_session.attempts.count()
        total_questions = Question.objects.filter(
            topic=active_session.topic,
            is_active=True
        ).count()
        progress = (
            round((answered_questions / total_questions) * 100, 0)
            if total_questions > 0
            else 0
        )
        
        active_session_data = {
            'id': active_session.id,
            'topic': active_session.topic,
            'topic_name': active_session.topic.name,
            'progress': progress,
            'answered_questions': answered_questions,
            'total_questions': total_questions,
            'remaining_questions': max(total_questions - answered_questions, 0),
        }

    # ===== FR-02-09: UPCOMING MOCK TEST REMINDERS =====
    # (Placeholder - will be implemented when mock tests are added)
    upcoming_mock_tests = []

    # ===== FR-02-10: STREAK COUNTER =====
    streak_days = 0
    check_date = today
    while True:
        day_start = timezone.make_aware(
            timezone.datetime.combine(check_date, timezone.datetime.min.time())
        )
        day_end = timezone.make_aware(
            timezone.datetime.combine(check_date + timedelta(days=1), timezone.datetime.min.time())
        )
        has_activity = PracticeSession.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        ).exists()
        
        if has_activity:
            streak_days += 1
            check_date -= timedelta(days=1)
        else:
            break

    # ===== RECENT SESSIONS =====
    recent_sessions = []
    for session in sessions.select_related(
        "topic__chapter__subject",
    ).order_by("-created_at", "-id")[:10]:
        
        session_attempts = session.attempts.all()
        answered_count = session_attempts.count()
        correct_count = session_attempts.filter(is_correct=True).count()
        
        recent_sessions.append({
            'id': session.id,
            'topic_name': session.topic.name,
            'chapter_name': session.topic.chapter.name,
            'subject_name': session.topic.chapter.subject.name,
            'status': session.status,
            'created_at': session.created_at,
            'answered_questions': answered_count,
            'correct_questions': correct_count,
            'status_display': session.get_status_display(),
        })

    # ===== RECENT PERFORMANCE =====
    recent_performance = []
    completed = sessions.filter(status=PracticeSession.Status.COMPLETED).order_by('-completed_at')[:5]
    for session in completed:
        attempts_count = session.attempts.count()
        if attempts_count > 0:
            correct = session.attempts.filter(is_correct=True).count()
            score = round((correct / attempts_count) * 100, 0)
            recent_performance.append({
                'name': session.topic.name[:25],
                'score': score
            })

    # ===== XP CALCULATIONS =====
    xp_earned = total_attempts * 5
    xp_goal = 200
    xp_progress = min(round((xp_earned / xp_goal) * 100), 100) if xp_goal > 0 else 0

    return {
        # Basic stats
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "active_sessions": active_sessions,
        "total_attempts": total_attempts,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "accuracy": accuracy,
        
        # FR-02-02: Today's questions
        "today_attempts": today_attempts,
        
        # FR-02-04: Study time this week
        "study_time": study_time_display,
        "study_time_minutes": study_time_minutes,
        
        # FR-02-05: Leaderboard rank
        "user_rank": user_rank,
        
        # FR-02-06: Subject performance
        "subject_performance": subject_performance,
        
        # FR-02-07: Weakest topics
        "weak_topics": weak_topics,
        
        # FR-02-08: Continue where you left off
        "active_session": active_session_data,
        
        # FR-02-09: Upcoming mock tests
        "upcoming_mock_tests": upcoming_mock_tests,
        
        # FR-02-10: Streak
        "streak_days": streak_days,
        
        # Other data
        "recent_sessions": recent_sessions,
        "recent_performance": recent_performance,
        "xp_earned": xp_earned,
        "xp_goal": xp_goal,
        "xp_progress": xp_progress,
        "completed_goals": 1,
        "total_goals": 3,
    }