from unittest import result

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse

from apps.core.models import Topic
from .models import ConceptExplanation, Doubt
from .services import ConceptExplainer, GrokDoubtSolver
from apps.core.models import Question
from .services import QuestionExplainer

@login_required
def doubt_solver(request):
    """Main doubt solver page."""
    doubts_list = Doubt.objects.filter(user=request.user)
    paginator = Paginator(doubts_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_doubts': doubts_list.count(),
    }
    return render(request, 'doubt_solver/solver.html', context)


@login_required
def ask_doubt(request):
    """Handle doubt submission and get AI answer."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    question = request.POST.get('question', '').strip()
    
    if not question:
        return JsonResponse({'error': 'Please enter your question.'}, status=400)
    
    if len(question) > 1000:
        return JsonResponse({'error': 'Question must be under 1000 characters.'}, status=400)
    
    doubt = Doubt.objects.create(
        user=request.user,
        question=question,
    )
    
    try:
        solver = GrokDoubtSolver()
        result = solver.get_answer(question)
        
        if result['success']:
            doubt.answer = result['answer']
            doubt.is_resolved = True
            doubt.save()
            
            return JsonResponse({
                'success': True,
                'answer': result['answer'],
                'doubt_id': doubt.id,
            })
        else:
            doubt.is_resolved = False
            doubt.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Unable to get answer. Please try again.',
            }, status=500)
            
    except ValueError as e:
        doubt.is_resolved = False
        doubt.save()
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)
    except Exception as e:
        doubt.is_resolved = False
        doubt.save()
        return JsonResponse({
            'success': False,
            'error': 'AI service unavailable. Please try again later.',
        }, status=500)

    # apps/doubt_solver/views.py - In the ask_doubt view

    if result['success']:
        doubt.answer = result['answer']
        doubt.is_resolved = True
        doubt.save()
        return JsonResponse({
            'success': True,
            'answer': result['answer'],
            'doubt_id': doubt.id,
        })
    else:
        doubt.is_resolved = False
        doubt.save()
        # Show the REAL error (temporarily for debugging)
        return JsonResponse({
            'success': False,
            'error': f"Debug: {result.get('error', 'Unknown')}",
        }, status=500)


@login_required
def delete_doubt(request, doubt_id):
    """Delete a doubt from history."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    doubt = get_object_or_404(Doubt, id=doubt_id, user=request.user)
    doubt.delete()
    
    return JsonResponse({'success': True})

@login_required
def explain_topic(request, topic_id):
    """Get or generate AI explanation for a topic (FR-08)."""
    topic = get_object_or_404(Topic, id=topic_id, is_active=True)
    
    # Check for cached explanation (FR-08-05)
    try:
        cached = ConceptExplanation.objects.get(topic=topic, is_valid=True)
        if not cached.is_expired():
            return JsonResponse({
                'success': True,
                'explanation': cached.explanation,
                'cached': True,
            })
    except ConceptExplanation.DoesNotExist:
        pass
    
    # Generate new explanation
    explainer = ConceptExplainer()
    result = explainer.explain_topic(
        topic_name=topic.name,
        chapter_name=topic.chapter.name,
        subject_name=topic.chapter.subject.name,
    )
    
    if result['success']:
        # Save or update cache (FR-08-05)
        ConceptExplanation.objects.update_or_create(
            topic=topic,
            defaults={
                'explanation': result['explanation'],
                'is_valid': True,
            }
        )
        
        return JsonResponse({
            'success': True,
            'explanation': result['explanation'],
            'cached': False,
        })
    else:
        # FR-08-07: Graceful error handling
        return JsonResponse({
            'success': False,
            'error': 'Unable to generate explanation. Please try again.',
        }, status=500)


@login_required
def regenerate_explanation(request, topic_id):
    """Regenerate explanation, bypassing cache (FR-08-06)."""
    topic = get_object_or_404(Topic, id=topic_id, is_active=True)
    
    # Invalidate cache
    ConceptExplanation.objects.filter(topic=topic).update(is_valid=False)
    
    # Generate new explanation
    explainer = ConceptExplainer()
    result = explainer.explain_topic(
        topic_name=topic.name,
        chapter_name=topic.chapter.name,
        subject_name=topic.chapter.subject.name,
    )
    
    if result['success']:
        ConceptExplanation.objects.update_or_create(
            topic=topic,
            defaults={
                'explanation': result['explanation'],
                'is_valid': True,
            }
        )
        
        return JsonResponse({
            'success': True,
            'explanation': result['explanation'],
            'cached': False,
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Unable to regenerate explanation. Please try again.',
        }, status=500)

@login_required
def explain_question_view(request, question_id):
    """Generate an explanation for a specific question and student's answer."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    question = get_object_or_404(Question, id=question_id, is_active=True)
    student_answer = request.POST.get('student_answer', '').upper()
    
    if not student_answer:
        return JsonResponse({'error': 'No answer provided.'}, status=400)
    
    explainer = QuestionExplainer()
    result = explainer.explain_question(question, student_answer)
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'explanation': result['explanation'],
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Unable to generate explanation. Please try again.',
        }, status=500)