# local_llm/inference.py
import torch
from typing import List, Dict, Optional
import time

class LocalInferenceEngine:
    """Run inference with local models"""
    
    def __init__(self, model, tokenizer, max_length: int = 2048):
        self.model = model
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.device = torch.cuda.current_device() if torch.cuda.is_available() else "cpu"
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        max_new_tokens: int = 512,
        repetition_penalty: float = 1.1,
        do_sample: bool = True,
        seed: Optional[int] = None
    ) -> str:
        """Generate text with local model"""
        
        if seed is not None:
            torch.manual_seed(seed)
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length - max_new_tokens
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )
        
        return response.strip()
    
    def generate_batch(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[str]:
        """Generate multiple responses"""
        responses = []
        for prompt in prompts:
            response = self.generate(prompt, **kwargs)
            responses.append(response)
        return responses