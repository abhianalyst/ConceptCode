from django.conf import settings
from openai import OpenAI

from question_generator.generation.openai_provider import (
    OpenAIQuestionProvider,
)


def get_openai_question_provider() -> OpenAIQuestionProvider:
    """Build an OpenAI-backed question provider from Django settings."""

    api_key = settings.OPENAI_API_KEY
    model = settings.OPENAI_MODEL

    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("OPENAI_API_KEY is not configured")

    if not isinstance(model, str) or not model.strip():
        raise ValueError("OPENAI_MODEL is not configured")

    client = OpenAI(api_key=api_key)

    return OpenAIQuestionProvider(
        client,
        model=model,
    )
