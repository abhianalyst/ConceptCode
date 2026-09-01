from django.test import SimpleTestCase

from question_generator.generation import (
    LLMQuestionGenerator,
    MockQuestionGenerator,
    QuestionGenerationService,
    build_generation_context,
)
from question_generator.generation.pipeline import (
    generate_questions_from_sections,
)
from question_generator.schemas import Question, Section


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

    def make_question(self, text):
        return Question(
            question=text,
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
            chapter="Biotechnology: Principles and Processes",
            topic="PRINCIPLES OF BIOTECHNOLOGY",
            source="biology_12.pdf",
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

    def test_rejects_empty_subject(self):
        generator = LLMQuestionGenerator(
            lambda context: []
        )

        service = QuestionGenerationService(
            generator
        )

        with self.assertRaises(ValueError):
            generate_questions_from_sections(
                [self.section],
                subject="",
                source="biology_12.pdf",
                service=service,
            )

    def test_rejects_empty_source(self):
        generator = LLMQuestionGenerator(
            lambda context: []
        )

        service = QuestionGenerationService(
            generator
        )

        with self.assertRaises(ValueError):
            generate_questions_from_sections(
                [self.section],
                subject="Biology",
                source="",
                service=service,
            )

    def test_rejects_invalid_service(self):
        with self.assertRaises(TypeError):
            generate_questions_from_sections(
                [self.section],
                subject="Biology",
                source="biology_12.pdf",
                service=None,
            )

    def test_generates_questions_from_multiple_sections(self):
        section1 = self.section

        section2 = Section(
            section_id="biology_12.pdf-11.2",
            number="11.2",
            title="PROCESSES OF BIOTECHNOLOGY",
            text=(
                "Biotechnology uses biological systems "
                "for useful applications."
            ),
            source="biology_12.pdf",
            page_start=206,
            page_end=208,
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
        )

        question1 = self.make_question(
            "What does biotechnology use?"
        )

        question2 = self.make_question(
            "Which field uses biological systems?"
        )

        generator = LLMQuestionGenerator(
            lambda context: (
                [question1]
                if context.topic == "PRINCIPLES OF BIOTECHNOLOGY"
                else [question2]
            )
        )

        service = QuestionGenerationService(
            generator
        )

        questions = generate_questions_from_sections(
            [section1, section2],
            subject="Biology",
            source="biology_12.pdf",
            service=service,
        )

        self.assertEqual(
            len(questions),
            2,
        )

    def test_removes_duplicates_across_sections(self):
        section1 = self.section

        section2 = Section(
            section_id="biology_12.pdf-11.2",
            number="11.2",
            title="PROCESSES OF BIOTECHNOLOGY",
            text=(
                "Biotechnology uses biological systems "
                "for useful applications."
            ),
            source="biology_12.pdf",
            page_start=206,
            page_end=208,
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
        )

        duplicate1 = self.make_question(
            "What carries genetic information?"
        )

        duplicate2 = self.make_question(
            "  WHAT   CARRIES genetic information?  "
        )

        generator = LLMQuestionGenerator(
            lambda context: (
                [duplicate1]
                if context.topic == "PRINCIPLES OF BIOTECHNOLOGY"
                else [duplicate2]
            )
        )

        service = QuestionGenerationService(
            generator
        )

        questions = generate_questions_from_sections(
            [section1, section2],
            subject="Biology",
            source="biology_12.pdf",
            service=service,
        )

        self.assertEqual(
            len(questions),
            1,
        )