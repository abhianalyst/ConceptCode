from unittest.mock import Mock, patch

from django.test import TestCase

from apps.core.models import Chapter, Subject, Topic
from apps.core.services.question_generation import (
generate_questions_for_section,
get_question_generation_service,
)
from question_generator.generation import (
QuestionGenerationService,
)
from question_generator.schemas import Question, Section
from question_generator.chunking import Chunk
from question_generator.generation.context import GenerationContext

class CoreQuestionGenerationTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(
            name="Biology",
        )

        self.chapter = Chapter.objects.create(
            subject=self.subject,
            unit_number=12,
            name="Molecular Basis of Inheritance",
        )

        self.topic = Topic.objects.create(
            chapter=self.chapter,
            name="DNA",
        )

        self.section = Section(
            section_id="biology_12.pdf-12.1",
            number="12.1",
            title="DNA",
            text="DNA carries genetic information.",
            source="biology_12.pdf",
            page_start=10,
            page_end=10,
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
        )

        self.question = Question(
            question="What carries genetic information?",
            options=[
                "DNA",
                "RNA",
                "Protein",
                "Lipid",
            ],
            correct_answer="DNA",
            explanation="DNA carries genetic information.",
            difficulty="Easy",
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
        )

    def make_service(self):
        generator = Mock()
        generator.generate.return_value = [self.question]

        service = Mock(spec=QuestionGenerationService)
        service.generate.return_value = [self.question]

        return service

    def test_returns_question_generation_service(self):
        provider = Mock()
        provider.generate.return_value = []

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
        provider = Mock()
        provider.generate.return_value = []

        with patch(
            "apps.core.services.question_generation."
            "get_gemini_question_provider",
            return_value=provider,
        ) as mock_get_provider:
            service = get_question_generation_service()

        mock_get_provider.assert_called_once()

        self.assertIsNotNone(
            service.generator,
        )

    def test_service_generates_questions_through_gemini_provider(self):
        provider = Mock()
        provider.generate.return_value = [self.question]

        with patch(
            "apps.core.services.question_generation."
            "get_gemini_question_provider",
            return_value=provider,
        ):
            service = get_question_generation_service()

        context = GenerationContext(
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
            chunks=[
                Chunk(
                    chunk_id="test-1",
                    text="DNA carries genetic information.",
                    source="biology_12.pdf",
                    page_start=10,
                    page_end=10,
                    subject="Biology",
                    chapter="Molecular Basis of Inheritance",
                    topic="DNA",
                )
            ],
        )

        questions = service.generate(context)

        provider.generate.assert_called_once_with(context)

        self.assertEqual(
            len(questions),
            1,
        )

        self.assertEqual(
            questions[0].question,
            "What carries genetic information?",
        )

    def test_generate_questions_for_section_uses_injected_service(self):
        service = self.make_service()

        saved_questions = generate_questions_for_section(
            self.section,
            topic=self.topic,
            service=service,
        )

        self.assertEqual(
            len(saved_questions),
            1,
        )

        self.assertEqual(
            saved_questions[0].question,
            "What carries genetic information?",
        )

        service.generate.assert_called_once()

    def test_generate_questions_for_section_persists_question(self):
        service = self.make_service()

        saved_questions = generate_questions_for_section(
            self.section,
            topic=self.topic,
            service=service,
        )

        self.assertEqual(
            self.topic.questions.count(),
            1,
        )

        saved = saved_questions[0]

        self.assertEqual(
            saved.topic,
            self.topic,
        )

        self.assertEqual(
            saved.option_a,
            "DNA",
        )

        self.assertEqual(
            saved.correct_answer,
            "DNA",
        )

    def test_generate_questions_for_section_creates_default_service(self):
        service = self.make_service()

        with patch(
            "apps.core.services.question_generation."
            "get_question_generation_service",
            return_value=service,
        ) as mock_get_service:
            saved_questions = generate_questions_for_section(
                self.section,
                topic=self.topic,
            )

        mock_get_service.assert_called_once()

        self.assertEqual(
            len(saved_questions),
            1,
        )

        self.assertEqual(
            saved_questions[0].question,
            "What carries genetic information?",
        )

    def test_generate_questions_for_section_rejects_invalid_section(self):
        service = self.make_service()

        with self.assertRaises(TypeError):
            generate_questions_for_section(
                "invalid",
                topic=self.topic,
                service=service,
            )

    def test_generate_questions_for_section_rejects_invalid_topic(self):
        service = self.make_service()

        with self.assertRaises(TypeError):
            generate_questions_for_section(
                self.section,
                topic=None,
                service=service,
            )

    def test_generate_questions_for_section_rejects_invalid_service(self):
        with self.assertRaises(TypeError):
            generate_questions_for_section(
                self.section,
                topic=self.topic,
                service="invalid",
            )
