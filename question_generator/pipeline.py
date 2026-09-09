# pipeline.py (Modified - Local Only)
from typing import List, Optional
from schemas.question import Question
from generation.local_generator import LocalQuestionGenerator
from rag.vector_store import LocalVectorStore
from rag.retriever import TextbookRetriever
from local_llm.model_loader import LocalModelLoader
from local_llm.inference import LocalInferenceEngine
from local_llm.embedding_loader import LocalEmbeddingManager
from generation.prompt_builder import PromptBuilder
from generation.question_factory import QuestionFactory
from validation.validator import QuestionValidator
from chunking.chunker import Chunker
import json
from pathlib import Path

class LocalQuestionPipeline:
    """Complete local question generation pipeline"""
    
    def __init__(self, config_path: str = "./config/settings.py"):
        self.config = self._load_config(config_path)
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all components"""
        
        # 1. Initialize model loader
        self.model_loader = LocalModelLoader(self.config['models_path'])
        
        # 2. Load LLM model
        self.llm_model, self.tokenizer = self.model_loader.load_llm_model(
            model_name=self.config['llm_model'],
            quantization=self.config['quantization']
        )
        
        # 3. Initialize inference engine
        self.llm_engine = LocalInferenceEngine(
            self.llm_model,
            self.tokenizer,
            max_length=self.config['max_length']
        )
        
        # 4. Load embedding model
        self.embedding_manager = LocalEmbeddingManager(
            model_path=f"{self.config['models_path']}/embeddings/{self.config['embedding_model']}"
        )
        
        # 5. Initialize vector store
        self.vector_store = LocalVectorStore(self.config['vector_db_path'])
        
        # 6. Initialize retriever
        self.retriever = TextbookRetriever(
            self.vector_store,
            self.embedding_manager
        )
        
        # 7. Initialize prompt builder
        self.prompt_builder = PromptBuilder()
        
        # 8. Initialize question factory
        self.question_factory = QuestionFactory()
        
        # 9. Initialize validator
        self.validator = QuestionValidator()
        
        # 10. Initialize main generator
        self.generator = LocalQuestionGenerator(
            llm_engine=self.llm_engine,
            retriever=self.retriever,
            prompt_builder=self.prompt_builder,
            question_factory=self.question_factory,
            validator=self.validator
        )
    
    def generate_questions(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: List[str] = None,
        subtopic: Optional[str] = None
    ) -> List[Question]:
        """Generate questions using local pipeline"""
        
        return self.generator.generate_questions(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=question_types,
            subtopic=subtopic
        )
    
    def setup_rag_pipeline(self, textbook_json_path: str):
        """Setup RAG pipeline with textbook content"""
        
        # Load textbook
        with open(textbook_json_path, 'r') as f:
            textbook_data = json.load(f)
        
        # Process with existing chunker
        chunker = Chunker()
        chunks = chunker.chunk_document(textbook_data)
        
        # Generate embeddings and add to vector store
        documents = []
        embeddings = []
        
        for chunk in chunks:
            documents.append({
                'content': chunk['content'],
                'metadata': chunk.get('metadata', {}),
                'chunk_id': chunk.get('id', f"chunk_{len(documents)}"),
                'chapter': chunk.get('chapter', ''),
                'topic': chunk.get('topic', '')
            })
            
            # Generate embedding
            embedding = self.embedding_manager.embed_text(chunk['content'])
            embeddings.append(embedding)
        
        # Store in vector database
        self.vector_store.add_documents(documents, embeddings)
        
        print(f"Added {len(documents)} chunks to vector store")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        
        default_config = {
            'models_path': './models',
            'llm_model': 'mistral-7b',
            'embedding_model': 'all-MiniLM-L6-v2',
            'quantization': 'q4_k_m',
            'max_length': 2048,
            'vector_db_path': './data/vector_store.db'
        }
        
        # Try to load custom config
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("settings", config_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Merge with default
                config = {**default_config}
                for key in default_config:
                    if hasattr(module, key):
                        config[key] = getattr(module, key)
                return config
        except Exception:
            pass
        
        return default_config