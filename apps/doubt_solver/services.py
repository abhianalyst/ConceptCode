# apps/doubt_solver/services.py

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class GrokDoubtSolver:
    """Service for solving NEET doubts using Groq API."""
    
    SYSTEM_PROMPT = """You are ConceptCode AI, a helpful NEET tutor.
You help students preparing for NEET (National Eligibility cum Entrance Test) in India.

Guidelines:
1. Answer questions related to Physics, Chemistry, and Biology (NEET syllabus only).
2. Provide clear, accurate explanations suitable for NEET aspirants.
3. Use simple language and provide examples where helpful.
4. If a question is NOT related to NEET subjects, politely decline:
   "I can only help with NEET-related subjects (Physics, Chemistry, Biology)."
5. Format your answers with proper structure:
   - Use bullet points for lists
   - Use **bold** for key terms
   - Keep answers concise but complete

Remember: You are helping a student prepare for a competitive exam. Be encouraging and supportive."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file."
            )
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        # ✅ UPDATED: Use the new valid model
        self.model = "openai/gpt-oss-120b"
    
    def get_answer(self, question):
        """Send a question to Groq and get an answer."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": question}
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            
            answer = response.choices[0].message.content
            
            return {
                'answer': answer,
                'success': True,
            }
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Groq API error: {error_msg}")
            print(f"\n❌ GROQ ERROR: {error_msg}\n")
            
            return {
                'answer': '',
                'success': False,
                'error': error_msg
            }