# scripts/download_models.py
import os
import subprocess
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer

def download_models():
    """Download all required models locally"""
    
    models_path = Path("./models")
    models_path.mkdir(parents=True, exist_ok=True)
    
    # Models to download
    models = {
        'llm': [
            {
                'name': 'mistral-7b',
                'repo': 'mistralai/Mistral-7B-Instruct-v0.2',
                'description': 'Main question generation model (7B params)'
            },
            {
                'name': 'llama-3-8b',
                'repo': 'meta-llama/Meta-Llama-3-8B-Instruct',
                'description': 'Alternative model (8B params)'
            },
            {
                'name': 'phi-3',
                'repo': 'microsoft/Phi-3-mini-4k-instruct',
                'description': 'Smaller model (3.8B params) - for low RAM'
            }
        ],
        'embeddings': [
            {
                'name': 'all-MiniLM-L6-v2',
                'repo': 'sentence-transformers/all-MiniLM-L6-v2',
                'description': 'Embedding model for RAG'
            }
        ]
    }
    
    print("Starting model downloads...")
    print(f"Models will be saved to: {models_path.absolute()}")
    
    # Download LLM models
    for model_info in models['llm']:
        print(f"\nDownloading {model_info['name']}...")
        print(f"Description: {model_info['description']}")
        
        model_dir = models_path / "llm" / model_info['name']
        model_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download model (using transformers)
            print(f"Downloading from {model_info['repo']}...")
            tokenizer = AutoTokenizer.from_pretrained(model_info['repo'])
            model = AutoModelForCausalLM.from_pretrained(
                model_info['repo'],
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Save locally
            model.save_pretrained(str(model_dir))
            tokenizer.save_pretrained(str(model_dir))
            
            print(f"✓ Successfully downloaded {model_info['name']}")
            
        except Exception as e:
            print(f"✗ Failed to download {model_info['name']}: {e}")
            print("Try running: pip install transformers accelerate bitsandbytes")
    
    # Download embedding models
    for model_info in models['embeddings']:
        print(f"\nDownloading {model_info['name']}...")
        print(f"Description: {model_info['description']}")
        
        model_dir = models_path / "embeddings" / model_info['name']
        model_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            model = SentenceTransformer(model_info['repo'])
            model.save(str(model_dir))
            print(f"✓ Successfully downloaded {model_info['name']}")
            
        except Exception as e:
            print(f"✗ Failed to download {model_info['name']}: {e}")
    
    print("\n✅ All models downloaded successfully!")
    print(f"Models are in: {models_path.absolute()}")

def check_models():
    """Check which models are already downloaded"""
    
    models_path = Path("./models")
    
    print("\nChecking downloaded models...")
    print("-" * 50)
    
    # Check LLM models
    llm_path = models_path / "llm"
    if llm_path.exists():
        models = [f for f in llm_path.iterdir() if f.is_dir()]
        print(f"LLM models found: {len(models)}")
        for model in models:
            size = sum(f.stat().st_size for f in model.rglob('*')) / (1024**3)
            print(f"  - {model.name}: {size:.1f} GB")
    else:
        print("No LLM models found")
    
    # Check embedding models
    embed_path = models_path / "embeddings"
    if embed_path.exists():
        models = [f for f in embed_path.iterdir() if f.is_dir()]
        print(f"Embedding models found: {len(models)}")
        for model in models:
            print(f"  - {model.name}")
    else:
        print("No embedding models found")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download local models")
    parser.add_argument('--check', action='store_true', help='Check downloaded models')
    parser.add_argument('--model', choices=['mistral-7b', 'llama-3-8b', 'phi-3'], 
                       help='Download specific model only')
    
    args = parser.parse_args()
    
    if args.check:
        check_models()
    else:
        download_models()