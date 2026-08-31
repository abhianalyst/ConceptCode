from django.core.serializers import python


python
from django.test import SimpleTestCase

from question_generator.generation import (
    MockQuestionGenerator,
    build_generation_context,
)
from question_generator.schemas import Section


class GenerationPipelineTests(SimpleTestCase):

    def setUp(self):
        self.section = Section(
            section_id="biology_12.pdf-11.1",
            number="11.1",
            title="PRINCIPLES OF BIOTECHNOLOGY",
            text=(
                "Biotechnology deals with techniques "
                "that use living organisms.\n\n"
                "Genetic engineering alters genetic material "
                "for useful purposes."
            ),
            source="biology_12.pdf",
            page_start=203,
            page_end=205,
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
        )

    def test_section_builds_generation_context(self):
        context = build_generation_context(
            self.section,
            subject="Biology",
            source="biology_12.pdf",
        )

        self.assertEqual(
            context.subject,
            "Biology",
        )

        self.assertEqual(
            context.chapter,
            "Biotechnology: Principles and Processes",
        )

        self.assertEqual(
            context.topic,
            "PRINCIPLES OF BIOTECHNOLOGY",
        )

        self.assertEqual(
            context.source,
            "biology_12.pdf",
        )

        self.assertTrue(context.chunks)

    def test_context_generates_questions(self):
        context = build_generation_context(
            self.section,
            subject="Biology",
            source="biology_12.pdf",
        )

        generator = MockQuestionGenerator(
            questions_per_context=2,
        )

        questions = generator.generate(context)

        self.assertEqual(
            len(questions),
            2,
        )

        for question in questions:
            self.assertEqual(
                question.subject,
                "Biology",
            )

            self.assertEqual(
                question.chapter,
                "Biotechnology: Principles and Processes",
            )

            self.assertEqual(
                question.topic,
                "PRINCIPLES OF BIOTECHNOLOGY",
            )

            self.assertEqual(
                question.source,
                "biology_12.pdf",
            )

            self.assertEqual(
                len(question.options),
                4,
            )

            self.assertIn(
                question.correct_answer,
                question.options,
            )

    def test_generated_question_contains_section_content(self):
        context = build_generation_context(
            self.section,
            subject="Biology",
            source="biology_12.pdf",
        )

        generator = MockQuestionGenerator()

        questions = generator.generate(context)

        self.assertTrue(questions)

        self.assertIn(
            "Biotechnology deals with techniques",
            questions[0].correct_answer,
        )

