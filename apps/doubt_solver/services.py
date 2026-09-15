# apps/doubt_solver/services.py

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class QuestionExplainer:
    """Service for generating explanations for specific practice questions."""
    
    SYSTEM_PROMPT = """You are ConceptCode AI, an expert NEET tutor.
A student is practicing a specific multiple-choice question and needs a detailed explanation for it.

You MUST follow this EXACT structure:

## 📖 Why This Answer is Correct
Explain in detail why the correct answer is right. Break down the reasoning.

## ❌ Why Other Options Are Wrong
Go through each incorrect option and explain why it is incorrect or a common misconception.

## 💡 Key Concept Behind This Question
Explain the underlying concept being tested. This helps the student learn for the future.

## ⚠️ Common Trap
Point out any tricky wording or common mistakes students make with this type of question.

## 🎯 NEET Relevance
Briefly mention why this concept is important for NEET.

Rules:
1. Be clear, specific, and educational.
2. Keep language simple and suitable for NEET aspirants.
3. Base your explanation on the provided question data.
4. Use the exact structure above with markdown formatting."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = "openai/gpt-oss-120b"
    
    def explain_question(self, question, student_answer):
        """Generate an explanation for a specific question."""
        prompt = f"""Explain this NEET practice question for a student who answered it.

**Question:**
{question.question}

**Options:**
A) {question.option_a}
B) {question.option_b}
C) {question.option_c}
D) {question.option_d}

**Correct Answer:** {question.correct_answer}

**Student's Answer:** {student_answer}

Provide a detailed, structured explanation based on the required format."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2000,
            )
            
            explanation = response.choices[0].message.content
            
            return {
                'explanation': explanation,
                'success': True,
            }
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Groq API error (question explainer): {error_msg}")
            return {
                'explanation': '',
                'success': False,
                'error': error_msg
            }

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

class ConceptExplainer:
    """Service for generating structured concept explanations using Groq API."""
    
    SYSTEM_PROMPT = """You are ConceptCode AI, an expert NEET tutor.
Your task is to explain NEET topics in a structured, easy-to-understand format.

You MUST follow this EXACT structure for every explanation:

## 📖 Overview
A brief 2-3 sentence introduction to the topic.

## 🔑 Key Concepts
- Important concept 1
- Important concept 2
- Important concept 3

## 📐 Important Formulas
List the relevant formulas (if applicable). If no formulas apply, write "No specific formulas for this topic."

## ⚠️ Common Mistakes
- Common mistake 1
- Common mistake 2

## 🎯 NEET Relevance
Explain why this topic is important for NEET and how often it appears.

Rules:
1. Only explain topics from Physics, Chemistry, and Biology.
2. Keep language simple and suitable for NEET aspirants.
3. Be accurate and exam-focused.
4. Use the exact structure above with markdown formatting.
5. Keep the total explanation under 800 words."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = "openai/gpt-oss-120b"
    
    def explain_topic(self, topic_name, chapter_name, subject_name):
        """Generate a structured explanation for a topic."""
        prompt = f"""Explain this NEET topic in detail:

Subject: {subject_name}
Chapter: {chapter_name}
Topic: {topic_name}

Generate a comprehensive yet concise explanation following the required structure."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000,
            )
            
            explanation = response.choices[0].message.content
            
            return {
                'explanation': explanation,
                'success': True,
            }
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Groq API error (concept explainer): {error_msg}")
            return {
                'explanation': '',
                'success': False,
                'error': error_msg
            }