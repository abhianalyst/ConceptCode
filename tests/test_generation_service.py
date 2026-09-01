from django.test import SimpleTestCase

from question_generator.generation.context import GenerationContext
from question_generator.generation.llm import LLMQuestionGenerator
from question_generator.generation.service import (
    QuestionGenerationService,
)
from question_generator.chunking import Chunk
from question_generator.schemas import Question


class GenerationServiceTests(SimpleTestCase):

    def setUp(self):
        self.context = GenerationContext(
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
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
        )

    def test_requires_generator(self):
        with self.assertRaises(TypeError):
            QuestionGenerationService(None)

    def test_rejects_invalid_context(self):
        generator = LLMQuestionGenerator(
            lambda context: []
        )

        service = QuestionGenerationService(generator)

        with self.assertRaises(TypeError):
            service.generate("invalid")

    def test_generates_questions(self):
        question = self.make_question(
            "What carries genetic information?"
        )

        generator = LLMQuestionGenerator(
            lambda context: [question]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        self.assertEqual(len(questions), 1)
        self.assertIsInstance(
            questions[0],
            Question,
        )

    def test_removes_duplicate_questions(self):
        question1 = self.make_question(
            "What carries genetic information?"
        )

        question2 = self.make_question(
            "  WHAT   CARRIES genetic information?  "
        )

        generator = LLMQuestionGenerator(
            lambda context: [
                question1,
                question2,
            ]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        self.assertEqual(len(questions), 1)

    def test_preserves_unique_questions(self):
        question1 = self.make_question(
            "What carries genetic information?"
        )

        question2 = self.make_question(
            "Which molecule stores hereditary information?"
        )

        generator = LLMQuestionGenerator(
            lambda context: [
                question1,
                question2,
            ]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        self.assertEqual(len(questions), 2)

    def test_rejects_invalid_question(self):
        question = Question(
            question="What carries genetic information?",
            options=[
                "DNA",
                "RNA",
                "Protein",
                "Lipid",
            ],
            correct_answer="DNA",
            explanation="",
            difficulty="Easy",
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
        )

        generator = LLMQuestionGenerator(
            lambda context: [question]
        )

        service = QuestionGenerationService(generator)

        with self.assertRaises(ValueError):
            service.generate(self.context)

    def test_preserves_generator_errors(self):
        def generate(context):
            raise RuntimeError("generation failed")

        generator = LLMQuestionGenerator(generate)

        service = QuestionGenerationService(generator)

        with self.assertRaises(RuntimeError):
            service.generate(self.context)