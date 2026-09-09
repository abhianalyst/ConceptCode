# apps/core/services/question_generation.py
"""
Question generation service.

Note: This is a stub. Full question generation requires the optional
question_generator module.
"""

import logging

logger = logging.getLogger(__name__)


def get_question_generation_service():
    """
    Get question generation service.
    
    This is a stub. Full implementation requires the optional
    question_generator module.
    
    Raises:
        ImportError: Always raises as this is a stub
    """
    raise ImportError(
        "Question generation service is not available. "
        "The question_generator module is optional and not currently installed. "
        "To use AI question generation, please install and configure question_generator."
    )


def generate_questions_for_section(section_data, num_questions=5):
    """
    Generate questions for a section.
    
    This is a stub. Full implementation requires the optional
    question_generator module.
    
    Raises:
        ImportError: Always raises as this is a stub
    """
    raise ImportError(
        "Question generation is not available. "
        "The question_generator module is optional and not currently installed. "
        "To use AI question generation, please install and configure question_generator."
    )


__all__ = [
    'get_question_generation_service',
    'generate_questions_for_section',
]