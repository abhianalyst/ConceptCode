from django.test import SimpleTestCase

from apps.core.services.biology_source import get_chapter_pages
from question_generator.generation import (
    MockQuestionGenerator,
    build_generation_context,
)
from question_generator.sections import extract_sections
from question_generator.schemas import Question


class BiologyGenerationIntegrationTests(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        pages = get_chapter_pages(
            "class_12",
            11,
        )

        cls.sections = extract_sections(
            pages,
            source="class_12_biology.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

    def test_real_biology_sections_build_generation_contexts(self):
        self.assertEqual(
            len(self.sections),
            3,
        )

        for section in self.sections:
            context = build_generation_context(
                section,
                subject="Biology",
                source="class_12_biology.pdf",
            )

            self.assertTrue(context.chunks)
            self.assertTrue(context.text.strip())

    def test_mock_generator_generates_from_real_section(self):
        section = self.sections[0]

        context = build_generation_context(
            section,
            subject="Biology",
            source="class_12_biology.pdf",
        )

        generator = MockQuestionGenerator()

        questions = generator.generate(context)

        self.assertEqual(
            len(questions),
            1,
        )

        self.assertIsInstance(
            questions[0],
            Question,
        )

        self.assertEqual(
            questions[0].subject,
            "Biology",
        )

        self.assertEqual(
            questions[0].topic,
            "PRINCIPLES OF BIOTECHNOLOGY",
        )

        self.assertEqual(
            questions[0].source,
            "class_12_biology.pdf",
        )

        self.assertEqual(
            len(questions[0].options),
            4,
        )

        self.assertIn(
            questions[0].correct_answer,
            questions[0].options,
        )
