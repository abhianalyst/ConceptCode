# question_generator/generation/__init__.py
"""
Question generation module.

Note: This module is optional and isolated from the core application.
"""

# Import providers (optional)
try:
    from .base import QuestionGenerator
except ImportError:
    QuestionGenerator = None

try:
    from .context import GenerationContext
except ImportError:
    GenerationContext = None

# Gemini provider (optional)
try:
    from .gemini_provider import GeminiQuestionProvider
except ImportError:
    GeminiQuestionProvider = None

# Ollama provider stub
try:
    from .ollama_provider import OllamaQuestionGenerator
except ImportError:
    OllamaQuestionGenerator = None

__all__ = [
    "QuestionGenerator",
    "GenerationContext",
    "GeminiQuestionProvider",
    "OllamaQuestionGenerator"
]