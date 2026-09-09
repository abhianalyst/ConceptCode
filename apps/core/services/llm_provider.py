# apps/core/services/llm_provider.py
"""
LLM Provider wrapper.

Note: This is a stub. Full LLM functionality requires the optional
question_generator module.
"""

import logging

logger = logging.getLogger(__name__)


def get_gemini_question_provider(*args, **kwargs):
    """
    Get Gemini question provider.
    
    This is a stub. Full implementation requires the optional
    question_generator module.
    
    Raises:
        ImportError: Always raises as this is a stub
    """
    raise ImportError(
        "LLM provider is not available. "
        "The question_generator module is optional and not currently installed. "
        "To use AI question generation, please install and configure question_generator."
    )


__all__ = [
    'get_gemini_question_provider',
]