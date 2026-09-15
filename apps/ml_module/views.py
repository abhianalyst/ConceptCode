from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import TopicPerformance
from .services import WeakAreaDetector


@login_required
def weak_areas_api(request):
    """API endpoint to get user's weak areas."""
    weak_topics = WeakAreaDetector.get_weak_topics(request.user, limit=5)
    
    data = [{
        'topic_id': p.topic.id,
        'topic_name': p.topic.name,
        'chapter_name': p.topic.chapter.name,
        'subject_name': p.topic.chapter.subject.name,
        'classification': p.classification,
        'accuracy': round(p.accuracy, 1),
        'attempts': p.attempts,
        'confidence': round(p.confidence * 100, 1),
        'priority': p.priority,
    } for p in weak_topics]
    
    return JsonResponse({
        'success': True,
        'weak_areas': data,
    })


@login_required
def recommended_topic_api(request):
    """API endpoint to get next recommended topic."""
    topic = WeakAreaDetector.get_recommended_topic(request.user)
    
    if topic:
        return JsonResponse({
            'success': True,
            'topic': {
                'id': topic.id,
                'name': topic.name,
                'chapter': topic.chapter.name,
                'subject': topic.chapter.subject.name,
            }
        })
    
    return JsonResponse({'success': False, 'message': 'No recommendation available'})