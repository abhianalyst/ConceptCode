# apps/core/services/biology_question_generation.py
"""
Biology question generation service.
This is a stub/placeholder - actual AI generation is optional.
"""

import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def generate_questions_from_biology_json(json_data: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Generate questions from biology JSON data.
    
    This is a stub implementation. Full AI generation requires the 
    question_generator module, which is optional.
    
    Args:
        json_data: JSON string containing biology content
        num_questions: Number of questions to generate
        
    Returns:
        List of question dictionaries
        
    Raises:
        NotImplementedError: This is a stub
    """
    logger.warning(
        "generate_questions_from_biology_json is a stub. "
        "Install and configure question_generator for AI question generation."
    )
    
    # Return empty list instead of failing
    return []


def generate_biology_questions(topic: str, content: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Generate biology questions from content.
    
    This is a stub implementation.
    
    Args:
        topic: The biology topic
        content: The content text
        num_questions: Number of questions to generate
        
    Returns:
        List of question dictionaries
    """
    logger.warning(
        f"generate_biology_questions is a stub. "
        f"Requested {num_questions} questions for topic '{topic}'."
    )
    
    return []


__all__ = [
    'generate_questions_from_biology_json',
    'generate_biology_questions',
]