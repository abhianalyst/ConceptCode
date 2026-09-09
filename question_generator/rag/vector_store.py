# rag/vector_store.py
import json
import pickle
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class LocalVectorStore:
    """Local vector database using SQLite + numpy"""
    
    def __init__(self, db_path: str = "./data/vector_store.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with vector support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                metadata TEXT,
                chunk_id TEXT,
                chapter TEXT,
                topic TEXT,
                embedding_path TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chapter_topic 
            ON documents(chapter, topic)
        ''')
        
        conn.commit()
        conn.close()
    
    def add_documents(
        self,
        documents: List[Dict],
        embeddings: List[np.ndarray]
    ):
        """Add documents with embeddings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for doc, embedding in zip(documents, embeddings):
            # Save embedding to file
            embed_id = doc.get('chunk_id', f"chunk_{id(doc)}")
            embed_path = f"./data/embeddings/{embed_id}.npy"
            
            Path("./data/embeddings").mkdir(parents=True, exist_ok=True)
            np.save(embed_path, embedding)
            
            # Insert document
            cursor.execute('''
                INSERT INTO documents 
                (content, metadata, chunk_id, chapter, topic, embedding_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                doc['content'],
                json.dumps(doc.get('metadata', {})),
                embed_id,
                doc.get('chapter', ''),
                doc.get('topic', ''),
                embed_path
            ))
        
        conn.commit()
        conn.close()
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        chapter_filter: Optional[str] = None,
        topic_filter: Optional[str] = None
    ) -> List[Dict]:
        """Search for similar documents"""
        
        # Load all embeddings from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT id, content, metadata, chunk_id, chapter, topic, embedding_path FROM documents"
        params = []
        
        conditions = []
        if chapter_filter:
            conditions.append("chapter = ?")
            params.append(chapter_filter)
        if topic_filter:
            conditions.append("topic = ?")
            params.append(topic_filter)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        # Compute similarities
        similarities = []
        for row in rows:
            embed_path = row[6]
            if Path(embed_path).exists():
                embedding = np.load(embed_path)
                similarity = np.dot(query_embedding, embedding)
                similarities.append(similarity)
            else:
                similarities.append(-1)
        
        # Get top k
        indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in indices:
            if similarities[idx] > 0:
                row = rows[idx]
                results.append({
                    'content': row[1],
                    'metadata': json.loads(row[2]),
                    'chunk_id': row[3],
                    'chapter': row[4],
                    'topic': row[5],
                    'similarity': float(similarities[idx])
                })
        
        return results