from unittest import result

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Doubt
from .services import GrokDoubtSolver


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