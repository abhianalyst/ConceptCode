# local_llm/model_loader.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import os
from typing import Optional, Dict

class LocalModelLoader:
    """Load and manage local models without external APIs"""
    
    def __init__(self, models_path: str = "./models"):
        self.models_path = models_path
        self.loaded_models = {}
        
    def load_llm_model(
        self,
        model_name: str = "mistral-7b",
        quantization: str = "q4_k_m",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        use_gpu: bool = True
    ) -> tuple:
        """Load a local LLM model for question generation"""
        
        # Model mappings - all local paths
        model_paths = {
            "mistral-7b": f"{self.models_path}/llm/mistral-7b",
            "llama-3-8b": f"{self.models_path}/llm/llama-3-8b",
            "phi-3": f"{self.models_path}/llm/phi-3",
            "tiny-llama": f"{self.models_path}/llm/tiny-llama"  # For low RAM
        }
        
        model_path = model_paths.get(model_name)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                f"Run download_models.py first."
            )
        
        # Load with quantization for memory efficiency
        if quantization == "q4_k_m":
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map="auto" if use_gpu else None,
                trust_remote_code=True
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if use_gpu else torch.float32,
                device_map="auto" if use_gpu else None
            )
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        return model, tokenizer
    
    def load_embedding_model(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ) -> SentenceTransformer:
        """Load local embedding model for RAG"""
        
        model_path = f"{self.models_path}/embeddings/{model_name}"
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Embedding model not found at {model_path}"
            )
        
        return SentenceTransformer(model_path)
    
    def get_model_info(self) -> Dict:
        """Get information about available models"""
        models_info = {}
        
        # Check which models are downloaded
        for model_type in ["llm", "embeddings"]:
            path = f"{self.models_path}/{model_type}"
            if os.path.exists(path):
                models_info[model_type] = os.listdir(path)
            else:
                models_info[model_type] = []
        
        return models_info