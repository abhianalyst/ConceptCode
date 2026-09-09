# generation/prompt_builder.py
from typing import List, Dict, Optional

class PromptBuilder:
    """Build structured prompts for local LLM"""
    
    def build_generation_prompt(
        self,
        topic: str,
        context: Dict,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: List[str] = None,
        subtopic: Optional[str] = None
    ) -> str:
        """Build comprehensive prompt for question generation"""
        
        # Prepare context
        main_content = "\n\n".join(context.get('main_content', []))
        related_content = "\n\n".join(context.get('related_content', []))
        
        # Build prompt
        prompt = f"""<|system|>
You are an expert question generator for {topic}.
Your task is to generate high-quality questions based on the textbook content provided.
Follow these rules:
1. Questions must be answerable from the textbook content
2. Use appropriate difficulty level: {difficulty}
3. Generate {num_questions} questions
4. If options are needed, provide 4 options
5. Structure: Question, Answer, Explanation (if needed)
6. Format output as JSON

<|user|>
Textbook Content:
{main_content}

{f"Related Concepts: {related_content}" if related_content else ""}

Topic: {topic}
{f"Subtopic: {subtopic}" if subtopic else ""}
Number of questions: {num_questions}
Difficulty: {difficulty}

Please generate {num_questions} questions following this JSON format:
{{
    "questions": [
        {{
            "question": "question text",
            "answer": "correct answer",
            "options": ["A", "B", "C", "D"],  // if MCQ
            "type": "MCQ|ShortAnswer|LongAnswer|Numerical",
            "difficulty": "Easy|Medium|Hard",
            "marks": 2,
            "explanation": "explanation of answer"
        }}
    ]
}}

<|assistant|>
"""
        return prompt
    
    def build_answer_prompt(
        self,
        question: str,
        context: Dict
    ) -> str:
        """Build prompt for answer generation"""
        
        main_content = "\n\n".join(context.get('main_content', []))
        
        prompt = f"""<|system|>
You are an expert answering questions based on textbook content.
Provide accurate, concise answers using only the provided content.

<|user|>
Context:
{main_content}

Question: {question}

Provide a clear and concise answer based on the context above.

<|assistant|>
"""
        return prompt
    
    def build_backup_prompt(
        self,
        topic: str,
        context: Dict,
        count: int
    ) -> str:
        """Simpler prompt for backup generation"""
        
        main_content = "\n\n".join(context.get('main_content', []))
        
        prompt = f"""<|system|>
Generate {count} simple questions about {topic} from the content below.

Content:
{main_content}

Format each question as:
Q: [question]
A: [answer]

<|assistant|>
"""
        return prompt