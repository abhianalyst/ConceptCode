from django.conf import settings
from google import genai

from question_generator.generation.gemini_provider import (
    GeminiQuestionProvider,
)


def get_gemini_question_provider() -> GeminiQuestionProvider:
    """Build a Gemini-backed question provider from Django settings."""

    api_key = settings.GEMINI_API_KEY
    model = settings.GEMINI_MODEL

    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("GEMINI_API_KEY is not configured")

    if not isinstance(model, str) or not model.strip():
        raise ValueError("GEMINI_MODEL is not configured")

    client = genai.Client(api_key=api_key)

    return GeminiQuestionProvider(
        client,
        model=model,
    )