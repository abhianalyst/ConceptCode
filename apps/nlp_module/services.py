"""
NLP & Semantic Search Service

Uses:
- Sentence-BERT (all-MiniLM-L6-v2) for text embeddings
- FAISS for fast similarity search
- Caches the FAISS index to disk for persistence
"""

import os
import pickle
import logging
import numpy as np
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy load to avoid loading model at import time
_model = None
_index = None
_content_items = []

# Paths for persistence
VECTOR_STORE_DIR = Path(__file__).parent / "vector_store"
VECTOR_STORE_DIR.mkdir(exist_ok=True)

FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.bin"
CONTENT_ITEMS_PATH = VECTOR_STORE_DIR / "content_items.pkl"

# Model config
MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim, fast, good quality
EMBEDDING_DIM = 384


class EmbeddingService:
    """Handles text to vector conversion using Sentence-BERT."""
    
    @staticmethod
    def get_model():
        """Get or load the Sentence-BERT model."""
        global _model
        if _model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading Sentence-BERT model: {MODEL_NAME}")
            _model = SentenceTransformer(MODEL_NAME)
        return _model
    
    @classmethod
    def encode(cls, texts, show_progress=False):
        """
        Convert text(s) to embeddings.
        
        Args:
            texts: str or list of str
            show_progress: whether to show progress bar
            
        Returns:
            numpy array of shape (n, 384)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        model = cls.get_model()
        embeddings = model.encode(
            texts,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True,  # Normalize for cosine similarity
        )
        return embeddings.astype('float32')


class ContentIndexer:
    """Builds and maintains the FAISS index of all searchable content."""
    
    @staticmethod
    def gather_content():
        """
        Gather all searchable content from the database.
        
        Returns:
            list of dicts: each dict has {id, type, text, metadata}
        """
        from apps.core.models import Question, Topic, Subject, Chapter
        
        content_items = []
        
        # ============================================================
        # 1. Questions
        # ============================================================
        logger.info("Gathering questions...")
        questions = Question.objects.filter(is_active=True).select_related(
            'topic__chapter__subject'
        )
        
        for q in questions:
            # Combine question + options + explanation for better search
            text_parts = [q.question]
            text_parts.append(f"A) {q.option_a}")
            text_parts.append(f"B) {q.option_b}")
            text_parts.append(f"C) {q.option_c}")
            text_parts.append(f"D) {q.option_d}")
            if q.explanation:
                text_parts.append(q.explanation)
            
            content_items.append({
                'id': q.id,
                'type': 'question',
                'text': ' '.join(text_parts),
                'display_text': q.question,
                'metadata': {
                    'subject': q.topic.chapter.subject.name,
                    'chapter': q.topic.chapter.name,
                    'topic': q.topic.name,
                    'difficulty': q.difficulty,
                    'topic_id': q.topic.id,
                }
            })
        
        # ============================================================
        # 2. Topics
        # ============================================================
        logger.info("Gathering topics...")
        topics = Topic.objects.filter(is_active=True).select_related(
            'chapter__subject'
        )
        
        for t in topics:
            content_items.append({
                'id': t.id,
                'type': 'topic',
                'text': f"{t.name} {t.chapter.name} {t.chapter.subject.name} {t.description or ''}",
                'display_text': t.name,
                'metadata': {
                    'subject': t.chapter.subject.name,
                    'chapter': t.chapter.name,
                    'description': t.description or '',
                    'topic_id': t.id,
                }
            })
        
        # ============================================================
        # 3. Chapters
        # ============================================================
        logger.info("Gathering chapters...")
        chapters = Chapter.objects.filter(is_active=True).select_related('subject')
        
        for c in chapters:
            content_items.append({
                'id': c.id,
                'type': 'chapter',
                'text': f"{c.name} {c.subject.name} {c.description or ''}",
                'display_text': c.name,
                'metadata': {
                    'subject': c.subject.name,
                    'unit_number': c.unit_number,
                    'description': c.description or '',
                }
            })
        
        # ============================================================
        # 4. Subjects
        # ============================================================
        logger.info("Gathering subjects...")
        subjects = Subject.objects.filter(is_active=True)
        
        for s in subjects:
            content_items.append({
                'id': s.id,
                'type': 'subject',
                'text': f"{s.name} {s.description or ''}",
                'display_text': s.name,
                'metadata': {
                    'description': s.description or '',
                }
            })
        
        logger.info(f"Total content items: {len(content_items)}")
        return content_items
    
    @classmethod
    def build_index(cls, show_progress=True):
        """
        Build the FAISS index from all content.
        
        Returns:
            dict: build statistics
        """
        import faiss
        
        # Step 1: Gather content
        content_items = cls.gather_content()
        
        if not content_items:
            logger.warning("No content to index")
            return {'count': 0}
        
        # Step 2: Create embeddings
        logger.info(f"Generating embeddings for {len(content_items)} items...")
        texts = [item['text'] for item in content_items]
        embeddings = EmbeddingService.encode(texts, show_progress=show_progress)
        
        # Step 3: Build FAISS index
        # Using IndexFlatIP for inner product (cosine similarity on normalized vectors)
        logger.info("Building FAISS index...")
        index = faiss.IndexFlatIP(EMBEDDING_DIM)
        index.add(embeddings)
        
        # Step 4: Save to disk
        logger.info(f"Saving index to {FAISS_INDEX_PATH}")
        faiss.write_index(index, str(FAISS_INDEX_PATH))
        
        with open(CONTENT_ITEMS_PATH, 'wb') as f:
            pickle.dump(content_items, f)
        
        # Step 5: Update in-memory cache
        global _index, _content_items
        _index = index
        _content_items = content_items
        
        logger.info("Index built successfully!")
        return {
            'count': len(content_items),
            'dimension': EMBEDDING_DIM,
        }
    
    @classmethod
    def load_index(cls, force_reload=False):
        """
        Load the FAISS index from disk.
        
        Args:
            force_reload: if True, reload even if already in memory
            
        Returns:
            bool: True if loaded successfully
        """
        import faiss
        
        global _index, _content_items
        
        # Already loaded in memory
        if _index is not None and _content_items and not force_reload:
            return True
        
        if not FAISS_INDEX_PATH.exists() or not CONTENT_ITEMS_PATH.exists():
            logger.warning(
                "No index found on disk. "
                "Run 'python manage.py build_search_index' to create it."
            )
            return False
        
        try:
            _index = faiss.read_index(str(FAISS_INDEX_PATH))
            with open(CONTENT_ITEMS_PATH, 'rb') as f:
                _content_items = pickle.load(f)
            logger.info(f"Index loaded: {len(_content_items)} items")
            return True
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    @classmethod
    def get_index(cls):
        """
        Get the loaded index. Auto-loads from disk if not in memory.
        
        Returns:
            tuple: (index, content_items)
        """
        # Auto-load if not already loaded
        if _index is None or not _content_items:
            cls.load_index()
        
        return _index, _content_items


class SemanticSearch:
    """Performs semantic search using the FAISS index."""
    
    @staticmethod
    def search(query, top_k=10, filter_type=None):
        """
        Search for content similar to the query.
        
        Args:
            query: search query string
            top_k: number of results to return
            filter_type: optional filter by content type (question, topic, chapter, subject)
            
        Returns:
            list of dicts: search results
        """
        # Auto-load index from disk if needed
        index, content_items = ContentIndexer.get_index()
        
        if index is None or not content_items:
            logger.warning("Search index not available")
            return []
        
        if not query or not query.strip():
            return []
        
        # Encode query
        query_embedding = EmbeddingService.encode(query)
        
        # Search
        # Request more results if filtering
        search_k = top_k * 3 if filter_type else top_k
        search_k = min(search_k, len(content_items))
        
        distances, indices = index.search(query_embedding, search_k)
        
        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(content_items):
                continue
            
            item = content_items[idx]
            
            # Apply filter
            if filter_type and item['type'] != filter_type:
                continue
            
            similarity = float(distances[0][i])
            
            results.append({
                'id': item['id'],
                'type': item['type'],
                'display_text': item['display_text'],
                'metadata': item['metadata'],
                'similarity': round(similarity * 100, 2),  # Percentage
            })
            
            if len(results) >= top_k:
                break
        
        return results
    
    @staticmethod
    def search_with_groups(query, top_k=5):
        """
        Search and group results by type.
        
        Returns:
            dict: { 'questions': [...], 'topics': [...], 'chapters': [...], 'subjects': [...] }
        """
        all_results = SemanticSearch.search(query, top_k=top_k * 4)
        
        grouped = {
            'questions': [],
            'topics': [],
            'chapters': [],
            'subjects': [],
        }
        
        for result in all_results:
            result_type = result['type']
            if result_type == 'question':
                grouped['questions'].append(result)
            elif result_type == 'topic':
                grouped['topics'].append(result)
            elif result_type == 'chapter':
                grouped['chapters'].append(result)
            elif result_type == 'subject':
                grouped['subjects'].append(result)
        
        # Trim to top_k per group
        for key in grouped:
            grouped[key] = grouped[key][:top_k]
        
        return grouped