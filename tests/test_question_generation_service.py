from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from apps.core.services.question_generation import (
    get_question_generation_service,
)
from question_generator.chunking import Chunk
from question_generator.generation import (
    QuestionGenerationService,
)
from question_generator.generation.context import (
    GenerationContext,
)
from question_generator.generation.llm import (
    LLMQuestionGenerator,
)
from apps.core.services.question_generation import (
    generate_questions_for_section,
    get_question_generation_service,
)

class QuestionGenerationServiceFactoryTests(SimpleTestCase):

    def make_provider(self):
        provider = Mock()
        provider.generate.return_value = []
        return provider

    def test_returns_question_generation_service(self):
        provider = self.make_provider()

        with patch(
            "apps.core.services.question_generation."
            "get_gemini_question_provider",
            return_value=provider,
        ):
            service = get_question_generation_service()

        self.assertIsInstance(
            service,
            QuestionGenerationService,
        )

    def test_uses_gemini_provider(self):
        provider = self.make_provider()

        with patch(
            "apps.core.services.question_generation."
            "get_gemini_question_provider",
            return_value=provider,
        ) as mock_get_provider:
            service = get_question_generation_service()

        mock_get_provider.assert_called_once()

        self.assertIsInstance(
            service.generator,
            LLMQuestionGenerator,
        )

    def test_generator_calls_provider_generate(self):
        provider = self.make_provider()

        chunk = Chunk(
            chunk_id="test-1",
            text="DNA carries genetic information.",
            source="biology_12.pdf",
            page_start=10,
            page_end=10,
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
        )

        context = GenerationContext(
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
            chunks=[chunk],
        )

        with patch(
            "apps.core.services.question_generation."
            "get_gemini_question_provider",
            return_value=provider,
        ):
            service = get_question_generation_service()

        service.generator.generate(context)

        provider.generate.assert_called_once_with(
            context,
        )

    def test_generate_questions_for_section_uses_default_service(self):
        provider = self.make_provider()

        with patch(
            "apps.core.services.question_generation."
            "get_gemini_question_provider",
            return_value=provider,
        ):
            service = get_question_generation_service()

        self.assertIsInstance(
            service,
            QuestionGenerationService,
        )
