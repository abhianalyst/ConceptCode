# generation/local_generator.py
from typing import List, Dict, Optional, Any
from schemas.question import Question, QuestionType, Difficulty
from .prompt_builder import PromptBuilder
from .question_factory import QuestionFactory
from rag.retriever import TextbookRetriever
from local_llm.inference import LocalInferenceEngine
from validation.validator import QuestionValidator
import json
import re

class LocalQuestionGenerator:
    """Main question generator using local LLM"""
    
    def __init__(
        self,
        llm_engine: LocalInferenceEngine,
        retriever: TextbookRetriever,
        prompt_builder: PromptBuilder,
        question_factory: QuestionFactory,
        validator: QuestionValidator
    ):
        self.llm = llm_engine
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.factory = question_factory
        self.validator = validator
    
    def generate_questions(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: List[str] = None,
        subtopic: Optional[str] = None,
        **kwargs
    ) -> List[Question]:
        """Generate questions from textbook content"""
        
        # 1. Retrieve relevant context
        context = self.retriever.retrieve_for_question(topic, subtopic)
        
        # 2. Build prompt
        prompt = self.prompt_builder.build_generation_prompt(
            topic=topic,
            subtopic=subtopic,
            context=context,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=question_types
        )
        
        # 3. Generate with local LLM
        raw_output = self.llm.generate(
            prompt,
            temperature=0.7,
            max_new_tokens=1024,
            repetition_penalty=1.1
        )
        
        # 4. Parse output
        parsed_questions = self._parse_llm_output(raw_output)
        
        # 5. Validate and filter
        validated_questions = []
        for q_data in parsed_questions:
            question = self.factory.create_question(
                question_data=q_data,
                topic=topic,
                context=context['main_content'][0] if context['main_content'] else None
            )
            
            # Validate
            if self.validator.validate_question(question):
                validated_questions.append(question)
        
        # 6. Ensure we have enough questions
        if len(validated_questions) < num_questions:
            # Try again with different prompt
            backup_questions = self._generate_backup_questions(
                topic, context, num_questions - len(validated_questions)
            )
            validated_questions.extend(backup_questions)
        
        return validated_questions[:num_questions]
    
    def _parse_llm_output(self, raw_output: str) -> List[Dict]:
        """Parse LLM output into structured question data"""
        
        questions = []
        
        # Try to parse JSON first
        try:
            # Look for JSON blocks
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            json_matches = re.findall(json_pattern, raw_output)
            
            if json_matches:
                for json_str in json_matches:
                    data = json.loads(json_str)
                    if isinstance(data, list):
                        questions.extend(data)
                    else:
                        questions.append(data)
            else:
                # Try direct JSON parsing
                data = json.loads(raw_output)
                if isinstance(data, list):
                    questions.extend(data)
                else:
                    questions.append(data)
        
        except json.JSONDecodeError:
            # Fallback: parse structured text
            questions = self._parse_structured_text(raw_output)
        
        return questions
    
    def _parse_structured_text(self, text: str) -> List[Dict]:
        """Parse structured text if JSON fails"""
        
        questions = []
        
        # Split by question markers
        q_blocks = re.split(r'Question\s*\d+[\.:]', text)
        
        for block in q_blocks[1:]:  # Skip header
            q_data = {}
            
            # Extract question
            q_match = re.search(r'(?i)question\s*[:\.]\s*(.*?)(?=Answer|$)', block, re.DOTALL)
            if q_match:
                q_data['question'] = q_match.group(1).strip()
            
            # Extract answer
            a_match = re.search(r'(?i)answer\s*[:\.]\s*(.*?)(?=Question|$)', block, re.DOTALL)
            if a_match:
                q_data['answer'] = a_match.group(1).strip()
            
            # Extract options if MCQ
            options = re.findall(r'([A-D])[\.\)]\s*(.*?)(?=[A-D][\.\)]|$)', block, re.DOTALL)
            if options:
                q_data['options'] = [opt[1].strip() for opt in options]
            
            if q_data.get('question'):
                questions.append(q_data)
        
        return questions
    
    def _generate_backup_questions(
        self,
        topic: str,
        context: Dict,
        count: int
    ) -> List[Question]:
        """Generate backup questions if primary generation fails"""
        
        backup_prompt = self.prompt_builder.build_backup_prompt(
            topic=topic,
            context=context,
            count=count
        )
        
        raw_output = self.llm.generate(
            backup_prompt,
            temperature=0.5,  # Lower temperature for more reliable output
            max_new_tokens=512
        )
        
        parsed = self._parse_llm_output(raw_output)
        
        questions = []
        for q_data in parsed[:count]:
            question = self.factory.create_question(
                question_data=q_data,
                topic=topic,
                context=context['main_content'][0] if context['main_content'] else None
            )
            if self.validator.validate_question(question):
                questions.append(question)
        
        return questions