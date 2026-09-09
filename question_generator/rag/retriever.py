# rag/retriever.py
from typing import List, Dict, Optional, Tuple
from .vector_store import LocalVectorStore
from local_llm.embedding_loader import LocalEmbeddingManager

class TextbookRetriever:
    """Retrieve relevant textbook content for question generation"""
    
    def __init__(
        self,
        vector_store: LocalVectorStore,
        embedding_manager: LocalEmbeddingManager
    ):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
    
    def retrieve(
        self,
        topic: str,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """Retrieve relevant content for a topic"""
        
        # Build query from topic
        query = f"topic: {topic}"
        if question_type:
            query += f" question_type: {question_type}"
        if difficulty:
            query += f" difficulty: {difficulty}"
        
        # Get embedding
        query_embedding = self.embedding_manager.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            topic_filter=topic
        )
        
        return results
    
    def retrieve_for_question(
        self,
        topic: str,
        subtopic: Optional[str] = None,
    ) -> Dict:
        """Retrieve comprehensive context for question generation"""
        
        # Get main content
        main_results = self.retrieve(topic, top_k=3)
        
        # Get related concepts if subtopic provided
        related_results = []
        if subtopic:
            related_results = self.retrieve(subtopic, top_k=2)
        
        # Combine and format
        context = {
            'main_content': [r['content'] for r in main_results],
            'related_content': [r['content'] for r in related_results],
            'main_chunks': main_results,
            'related_chunks': related_results
        }
        
        return context