from django.test import SimpleTestCase

from question_generator.chunking import Chunk
from question_generator.generation.context import GenerationContext
from question_generator.generation.gemini_provider import (
    GeminiQuestionProvider,
)
from question_generator.schemas import Question


class FakeModels:

    def generate_content(self, **kwargs):
        self.kwargs = kwargs

        return type(
            "FakeResponse",
            (),
            {
                "text": (
                    '{"questions": ['
                    '{'
                    '"question": "What carries genetic information?",'
                    '"options": ["DNA", "RNA", "Protein", "Lipid"],'
                    '"correct_answer": "DNA",'
                    '"explanation": "DNA carries genetic information.",'
                    '"difficulty": "Easy"'
                    '}'
                    ']}'
                )
            },
        )()


class FakeClient:

    def __init__(self):
        self.models = FakeModels()


class GeminiQuestionProviderTests(SimpleTestCase):

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

    def test_requires_client(self):
        with self.assertRaises(ValueError):
            GeminiQuestionProvider(
                None,
                model="test-model",
            )

    def test_requires_model(self):
        with self.assertRaises(ValueError):
            GeminiQuestionProvider(
                FakeClient(),
                model="",
            )

    def test_rejects_invalid_context(self):
        provider = GeminiQuestionProvider(
            FakeClient(),
            model="test-model",
        )

        with self.assertRaises(TypeError):
            provider.generate("invalid")

    def test_build_prompt_contains_context(self):
        prompt = GeminiQuestionProvider._build_prompt(
            self.context
        )

        self.assertIn("Biology", prompt)
        self.assertIn(
            "Molecular Basis of Inheritance",
            prompt,
        )
        self.assertIn("DNA", prompt)
        self.assertIn(
            "DNA carries genetic information.",
            prompt,
        )

    def test_generate_uses_configured_model(self):
        client = FakeClient()

        provider = GeminiQuestionProvider(
            client,
            model="gemini-test-model",
        )

        questions = provider.generate(self.context)

        self.assertEqual(
            client.models.kwargs["model"],
            "gemini-test-model",
        )

        self.assertEqual(len(questions), 1)

    def test_generate_uses_context_as_contents(self):
        client = FakeClient()

        provider = GeminiQuestionProvider(
            client,
            model="test-model",
        )

        provider.generate(self.context)

        contents = client.models.kwargs["contents"]

        self.assertIn(
            "DNA carries genetic information.",
            contents,
        )

    def test_generate_requests_json(self):
        client = FakeClient()

        provider = GeminiQuestionProvider(
            client,
            model="test-model",
        )

        provider.generate(self.context)

        config = client.models.kwargs["config"]

        self.assertEqual(
            config.response_mime_type,
            "application/json",
        )

        self.assertIsNotNone(
            config.response_schema,
        )

    def test_generate_returns_questions(self):
        provider = GeminiQuestionProvider(
            FakeClient(),
            model="test-model",
        )

        questions = provider.generate(self.context)

        self.assertEqual(len(questions), 1)

        question = questions[0]

        self.assertIsInstance(
            question,
            Question,
        )

        self.assertEqual(
            question.question,
            "What carries genetic information?",
        )

        self.assertEqual(
            question.correct_answer,
            "DNA",
        )

        self.assertEqual(
            question.subject,
            "Biology",
        )

        self.assertEqual(
            question.chapter,
            "Molecular Basis of Inheritance",
        )

        self.assertEqual(
            question.topic,
            "DNA",
        )

        self.assertEqual(
            question.source,
            "biology_12.pdf",
        )

    def test_parse_response_rejects_invalid_json(self):
        response = type(
            "FakeResponse",
            (),
            {
                "text": "not valid json",
            },
        )()

        with self.assertRaises(ValueError):
            GeminiQuestionProvider._parse_response(
                response,
                self.context,
            )

    def test_parse_response_rejects_missing_questions(self):
        response = type(
            "FakeResponse",
            (),
            {
                "text": "{}",
            },
        )()

        with self.assertRaises(ValueError):
            GeminiQuestionProvider._parse_response(
                response,
                self.context,
            )

    def test_parse_response_rejects_missing_text(self):
        response = type(
            "FakeResponse",
            (),
            {},
        )()

        with self.assertRaises(ValueError):
            GeminiQuestionProvider._parse_response(
                response,
                self.context,
            )