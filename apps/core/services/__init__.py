# apps/core/services/__init__.py
"""
Core services module for ConceptCode.
"""

# Import biology section services
from apps.core.services.biology_sections import (
    BiologySection,
    extract_sections,
)

# Import biology question generation (stub)
from apps.core.services.biology_question_generation import (
    generate_questions_from_biology_json,
)

# Note: LLM and question generation services are optional.
# The question_generator module is isolated and not required.

__all__ = [
    "BiologySection",
    "extract_sections",
    "generate_questions_from_biology_json",
]