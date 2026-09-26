from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .services import SemanticSearch
from .models import SearchLog
from django.shortcuts import render

@login_required
@require_GET
def search_api(request):
    """
    Semantic search API endpoint.
    
    Query params:
        q: search query
        type: optional filter (question, topic, chapter, subject)
        limit: number of results (default 10, max 50)
    """
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('type', '').strip() or None
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    if not query:
        return JsonResponse({'success': False, 'error': 'Query required'}, status=400)
    
    # Validate filter_type
    if filter_type and filter_type not in ['question', 'topic', 'chapter', 'subject']:
        filter_type = None
    
    try:
        # Group results by type (returns dict with questions, topics, etc.)
        grouped_results = SemanticSearch.search_with_groups(query, top_k=limit)
        
        # Flatten for count
        total_count = sum(len(items) for items in grouped_results.values())
        
        # Log search
        SearchLog.objects.create(
            query=query[:500],
            results_count=total_count,
            user_id=request.user.id,
        )
        
        return JsonResponse({
            'success': True,
            'query': query,
            'total': total_count,
            'results': grouped_results,
        })
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Search error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Search failed. Please try again.'
        }, status=500)

@login_required
def search_page(request):
    """Render the semantic search page."""
    return render(request, 'nlp_module/search.html')