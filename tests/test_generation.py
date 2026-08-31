from django.test import SimpleTestCase

from question_generator.chunking import Chunk
from question_generator.schemas import Question
from question_generator.generation import (
    GenerationContext,
    MockQuestionGenerator,
    QuestionGenerator,
)
from question_generator.generation.llm import LLMQuestionGenerator


class GenerationContextTests(SimpleTestCase):

    def setUp(self):
        self.chunk = Chunk(
            chunk_id="test-1",
            text="DNA carries genetic information.",
            source="biology_12.pdf",
            page_start=10,
            page_end=10,
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
        )

    def test_context_requires_chunks(self):
        with self.assertRaises(ValueError):
            GenerationContext(
                subject="Biology",
                chapter="Molecular Basis of Inheritance",
                topic="DNA",
                source="biology_12.pdf",
                chunks=[],
            )

    def test_context_rejects_non_chunks(self):
        with self.assertRaises(TypeError):
            GenerationContext(
                subject="Biology",
                chapter="Molecular Basis of Inheritance",
                topic="DNA",
                source="biology_12.pdf",
                chunks=["not a chunk"],
            )

    def test_context_combines_chunk_text(self):
        context = GenerationContext(
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
            chunks=[
                self.chunk,
                Chunk(
                    chunk_id="test-2",
                    text="DNA is composed of nucleotides.",
                    source="biology_12.pdf",
                    page_start=11,
                    page_end=11,
                    subject="Biology",
                    chapter="Molecular Basis of Inheritance",
                    topic="DNA",
                ),
            ],
        )

        self.assertEqual(
            context.text,
            (
                "DNA carries genetic information.\n\n"
                "DNA is composed of nucleotides."
            ),
        )


class MockQuestionGeneratorTests(SimpleTestCase):

    def setUp(self):
        self.chunk = Chunk(
            chunk_id="test-1",
            text="DNA carries genetic information.",
            source="biology_12.pdf",
            page_start=10,
            page_end=10,
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
        )

        self.context = GenerationContext(
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
            chunks=[self.chunk],
        )

    def test_generator_is_question_generator(self):
        generator = MockQuestionGenerator()

        self.assertIsInstance(
            generator,
            QuestionGenerator,
        )

    def test_generates_questions_from_context(self):
        generator = MockQuestionGenerator()

        questions = generator.generate(self.context)

        self.assertEqual(len(questions), 1)
        self.assertEqual(
            questions[0].chapter,
            "Molecular Basis of Inheritance",
        )
        self.assertEqual(
            questions[0].topic,
            "DNA",
        )
        self.assertEqual(
            questions[0].subject,
            "Biology",
        )

    def test_questions_per_context(self):
        generator = MockQuestionGenerator(
            questions_per_context=3,
        )

        questions = generator.generate(self.context)

        self.assertEqual(len(questions), 3)

    def test_generator_rejects_chunk(self):
        generator = MockQuestionGenerator()

        with self.assertRaises(TypeError):
            generator.generate(self.chunk)

    def test_generated_question_uses_context_content(self):
        generator = MockQuestionGenerator()

        questions = generator.generate(self.context)

        self.assertIn(
            "DNA carries genetic information",
            questions[0].options,
        )

        self.assertEqual(
            questions[0].correct_answer,
            "DNA carries genetic information",
        )

    def test_generator_rejects_invalid_questions_per_context(self):
        with self.assertRaises(ValueError):
            MockQuestionGenerator(questions_per_context=0)

        with self.assertRaises(ValueError):
            MockQuestionGenerator(questions_per_context=-1)

    def test_generated_questions_have_four_options(self):
        generator = MockQuestionGenerator(
            questions_per_context=2,
        )

        questions = generator.generate(self.context)

        for question in questions:
            self.assertEqual(len(question.options), 4)
            self.assertIn(
                question.correct_answer,
                question.options,
            )

    def test_generated_questions_preserve_source(self):
        generator = MockQuestionGenerator()

        questions = generator.generate(self.context)

        self.assertEqual(
            questions[0].source,
            "biology_12.pdf",
        )

    def test_generated_questions_have_difficulty(self):
        generator = MockQuestionGenerator()

        questions = generator.generate(self.context)

        self.assertEqual(
            questions[0].difficulty,
            "Easy",
        )

class LLMQuestionGeneratorTests(SimpleTestCase):

    def setUp(self):
        self.chunk = Chunk(
            chunk_id="test-1",
            text="DNA carries genetic information.",
            source="biology_12.pdf",
            page_start=10,
            page_end=10,
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
        )

        self.context = GenerationContext(
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
            chunks=[self.chunk],
        )

    def test_generator_is_question_generator(self):
        generator = LLMQuestionGenerator(
            lambda context: []
        )

        self.assertIsInstance(
            generator,
            QuestionGenerator,
        )

    def test_generator_calls_injected_function(self):
        called = []

        def generate_fn(context):
            called.append(context)
            return []

        generator = LLMQuestionGenerator(generate_fn)

        result = generator.generate(self.context)

        self.assertEqual(result, [])
        self.assertEqual(called, [self.context])

    def test_generator_rejects_invalid_context(self):
        generator = LLMQuestionGenerator(
            lambda context: []
        )

        with self.assertRaises(TypeError):
            generator.generate(self.chunk)

    def test_generator_rejects_non_list_result(self):
        generator = LLMQuestionGenerator(
            lambda context: "invalid"
        )

        with self.assertRaises(TypeError):
            generator.generate(self.context)

    def test_generator_rejects_invalid_question_objects(self):
        generator = LLMQuestionGenerator(
            lambda context: ["not a question"]
        )

        with self.assertRaises(TypeError):
            generator.generate(self.context)

    def test_generator_returns_questions(self):
        question = Question(
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

        generator = LLMQuestionGenerator(
            lambda context: [question]
        )

        questions = generator.generate(self.context)

        self.assertEqual(questions, [question]) 