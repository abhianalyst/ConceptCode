from django.test import SimpleTestCase

from question_generator.chunking import Chunk
from question_generator.generation.context import GenerationContext
from question_generator.generation.openai_provider import (
    OpenAIQuestionProvider,
)
from question_generator.schemas import Question

class FakeResponses:

    def create(self, **kwargs):
        self.kwargs = kwargs

        return type(
            "FakeResponse",
            (),
            {
                "output_text": (
                    '{"questions": []}'
                )
            },
        )()


class FakeClient:

    def __init__(self):
        self.responses = FakeResponses()


class OpenAIQuestionProviderTests(SimpleTestCase):

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
            OpenAIQuestionProvider(
                None,
                model="test-model",
            )

    def test_requires_model(self):
        with self.assertRaises(ValueError):
            OpenAIQuestionProvider(
                FakeClient(),
                model="",
            )

    def test_rejects_invalid_context(self):
        provider = OpenAIQuestionProvider(
            FakeClient(),
            model="test-model",
        )

        with self.assertRaises(TypeError):
            provider.generate("invalid")

    def test_build_prompt_contains_context(self):
        prompt = OpenAIQuestionProvider._build_prompt(
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

        provider = OpenAIQuestionProvider(
            client,
            model="test-model",
        )

        questions = provider.generate(self.context)

        self.assertEqual(questions, [])

        self.assertEqual(
            client.responses.kwargs["model"],
            "test-model",
        )


    def test_generate_uses_context_as_input(self):
        client = FakeClient()

        provider = OpenAIQuestionProvider(
            client,
            model="test-model",
        )

        provider.generate(self.context)

        prompt = client.responses.kwargs["input"]

        self.assertIn(
            "DNA carries genetic information.",
            prompt,
        )

    def test_generate_requests_structured_json(self):
        client = FakeClient()

        provider = OpenAIQuestionProvider(
            client,
            model="test-model",
        )

        provider.generate(self.context)

        self.assertIn(
            "text",
            client.responses.kwargs,
        )

        text_config = client.responses.kwargs["text"]

        self.assertEqual(
            text_config["format"]["type"],
            "json_schema",
        )

        self.assertEqual(
            text_config["format"]["name"],
            "question_generation",
        )

        self.assertTrue(
            text_config["format"]["strict"],
        )    

    def test_parse_response_returns_questions(self):
        response = type(
            "FakeResponse",
            (),
            {
                "output_text": (
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

        questions = OpenAIQuestionProvider._parse_response(
            response,
            self.context,
        )

        self.assertEqual(len(questions), 1)

        question = questions[0]

        self.assertIsInstance(question, Question)
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
                "output_text": "not valid json",
            },
        )()

        with self.assertRaises(ValueError):
            OpenAIQuestionProvider._parse_response(
                response,
                self.context,
            )

    def test_parse_response_rejects_missing_questions(self):
        response = type(
            "FakeResponse",
            (),
            {
                "output_text": "{}",
            },
        )()

        with self.assertRaises(ValueError):
            OpenAIQuestionProvider._parse_response(
                response,
                self.context,
            )