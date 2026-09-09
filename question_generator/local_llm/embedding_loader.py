# local_llm/embedding_loader.py
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
import pickle
from pathlib import Path

class LocalEmbeddingManager:
    """Manage embeddings for RAG"""
    
    def __init__(self, model_path: str, cache_path: str = "./cache/embeddings"):
        self.model = SentenceTransformer(model_path)
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text"""
        if isinstance(text, str):
            text = [text]
        
        return self.model.encode(text, normalize_embeddings=True)
    
    def embed_with_cache(
        self,
        text: Union[str, List[str]],
        cache_key: Optional[str] = None
    ) -> np.ndarray:
        """Embed with caching for speed"""
        
        if cache_key:
            cache_file = self.cache_path / f"{cache_key}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        embeddings = self.embed_text(text)
        
        if cache_key:
            with open(cache_file, 'wb') as f:
                pickle.dump(embeddings, f)
        
        return embeddings
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        embeddings: np.ndarray,
        top_k: int = 5
    ) -> List[int]:
        """Find most similar embeddings"""
        # Cosine similarity
        similarities = np.dot(embeddings, query_embedding)
        indices = np.argsort(similarities)[::-1][:top_k]
        return indices.tolist()