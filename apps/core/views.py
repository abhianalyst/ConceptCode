# apps/core/views.py
"""
Core views for ConceptCode.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from apps.core.models import Subject, Question, Topic, QuestionReport

User = get_user_model()


def home(request):
    """
    Home page view.
    Shows practice interface for students and admin dashboard quick access for admins.
    """
    # Get all active subjects with their chapters and topics
    subjects = Subject.objects.filter(is_active=True).prefetch_related(
        'chapters__topics'
    )
    
    # Get platform stats
    total_questions = Question.objects.count()
    total_users = User.objects.count()
    total_subjects = Subject.objects.count()
    total_topics = Topic.objects.count()
    
    context = {
        'subjects': subjects,
        'total_questions': total_questions,
        'total_users': total_users,
        'total_subjects': total_subjects,
        'total_topics': total_topics,
    }
    
    # Add admin stats if user is admin
    if request.user.is_authenticated and request.user.role == 'admin':
        pending_reports = QuestionReport.objects.filter(
            status=QuestionReport.ReportStatus.PENDING
        ).count()
        
        context.update({
            'total_questions': total_questions,
            'active_questions': Question.objects.filter(is_active=True).count(),
            'total_subjects': total_subjects,
            'total_topics': total_topics,
            'pending_reports': pending_reports,
            'total_users': total_users,
        })
    
    return render(request, 'core/home.html', context)


def about(request):
    """About page view."""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page view."""
    return render(request, 'core/contact.html')


def privacy(request):
    """Privacy policy page view."""
    return render(request, 'core/privacy.html')


def terms(request):
    """Terms of service page view."""
    return render(request, 'core/terms.html')


# Optional: Error handlers
def handler404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'core/404.html', status=404)


def handler500(request):
    """Custom 500 error handler."""
    return render(request, 'core/500.html', status=500)