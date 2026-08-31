from django.core.serializers import python


python
from django.test import SimpleTestCase

from apps.core.services.biology_source import get_chapter_pages
from question_generator.generation import (
    MockQuestionGenerator,
    build_generation_context,
)
from question_generator.sections import extract_sections


class RealGenerationPipelineTests(SimpleTestCase):

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

    def test_real_chapter_has_three_sections(self):
        self.assertEqual(
            len(self.sections),
            3,
        )

        self.assertEqual(
            [section.number for section in self.sections],
            ["11.1", "11.2", "11.3"],
        )

    def test_real_sections_build_generation_contexts(self):
        for section in self.sections:
            context = build_generation_context(
                section,
                subject="Biology",
                source="class_12_biology.pdf",
            )

            self.assertTrue(context.chunks)
            self.assertTrue(context.text.strip())

            self.assertEqual(
                context.subject,
                "Biology",
            )

            self.assertEqual(
                context.topic,
                section.title,
            )

    def test_real_sections_generate_questions(self):
        generator = MockQuestionGenerator()

        for section in self.sections:
            context = build_generation_context(
                section,
                subject="Biology",
                source="class_12_biology.pdf",
            )

            questions = generator.generate(context)

            self.assertEqual(
                len(questions),
                1,
            )

            question = questions[0]

            self.assertEqual(
                question.subject,
                "Biology",
            )

            self.assertEqual(
                question.topic,
                section.title,
            )

            self.assertEqual(
                question.source,
                "class_12_biology.pdf",
            )

            self.assertEqual(
                len(question.options),
                4,
            )

            self.assertIn(
                question.correct_answer,
                question.options,
            )
