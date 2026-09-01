from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase

from apps.core.services.llm_provider import (
    get_openai_question_provider,
)
from question_generator.generation.openai_provider import (
    OpenAIQuestionProvider,
)


class LLMProviderTests(SimpleTestCase):

    def test_returns_openai_question_provider(self):
        with patch(
            "apps.core.services.llm_provider.OpenAI"
        ) as mock_openai:
            provider = get_openai_question_provider()

        self.assertIsInstance(
            provider,
            OpenAIQuestionProvider,
        )

        mock_openai.assert_called_once_with(
            api_key=settings.OPENAI_API_KEY,
        )

        self.assertEqual(
            provider.model,
            settings.OPENAI_MODEL,
        )

    def test_requires_api_key(self):
        with patch.object(
            settings,
            "OPENAI_API_KEY",
            "",
        ):
            with self.assertRaises(ValueError):
                get_openai_question_provider()

    def test_requires_model(self):
        with patch.object(
            settings,
            "OPENAI_MODEL",
            "",
        ):
            with self.assertRaises(ValueError):
                get_openai_question_provider()
