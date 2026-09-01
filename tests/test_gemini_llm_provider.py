from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase

from apps.core.services.llm_provider import (
    get_gemini_question_provider,
)
from question_generator.generation.gemini_provider import (
    GeminiQuestionProvider,
)


class LLMProviderTests(SimpleTestCase):

    def test_returns_gemini_question_provider(self):
        with patch.object(
            settings,
            "GEMINI_API_KEY",
            "test-gemini-api-key",
        ), patch.object(
            settings,
            "GEMINI_MODEL",
            "gemini-test-model",
        ), patch(
            "apps.core.services.llm_provider.genai.Client"
        ) as mock_client:
            provider = get_gemini_question_provider()

        self.assertIsInstance(
            provider,
            GeminiQuestionProvider,
        )

        mock_client.assert_called_once_with(
            api_key="test-gemini-api-key",
        )

        self.assertEqual(
            provider.model,
            "gemini-test-model",
        )

    def test_requires_api_key(self):
        with patch.object(
            settings,
            "GEMINI_API_KEY",
            "",
        ):
            with self.assertRaises(ValueError):
                get_gemini_question_provider()

    def test_requires_model(self):
        with patch.object(
            settings,
            "GEMINI_MODEL",
            "",
        ):
            with self.assertRaises(ValueError):
                get_gemini_question_provider()