import json
from typing import Any

from google.genai import types

from question_generator.generation.context import GenerationContext
from question_generator.schemas import Question


QUESTION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "question": {"type": "STRING"},
                    "options": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                    },
                    "correct_answer": {"type": "STRING"},
                    "explanation": {"type": "STRING"},
                    "difficulty": {"type": "STRING"},
                },
                "required": [
                    "question",
                    "options",
                    "correct_answer",
                    "explanation",
                    "difficulty",
                ],
            },
        },
    },
    "required": ["questions"],
}


class GeminiQuestionProvider:
    """Provider adapter for Gemini-backed question generation."""

    def __init__(
        self,
        client: Any,
        *,
        model: str,
    ) -> None:
        if client is None:
            raise ValueError("client is required")

        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a non-empty string")

        self.client = client
        self.model = model

    def generate(
        self,
        context: GenerationContext,
    ) -> list[Question]:
        if not isinstance(context, GenerationContext):
            raise TypeError(
                "context must be a GenerationContext"
            )

        prompt = self._build_prompt(context)

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QUESTION_SCHEMA,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        return self._parse_response(response, context)

    @staticmethod
    def _build_prompt(
        context: GenerationContext,
    ) -> str:
        return (
            "Generate multiple-choice questions using only the "
            "provided textbook material.\n\n"
            "Rules:\n"
            "- Use only information supported by the textbook material.\n"
            "- Generate high-quality multiple-choice questions.\n"
            "- Every question must have exactly 4 options.\n"
            "- correct_answer must exactly match one option.\n"
            "- Include a concise explanation.\n"
            "- Assign an appropriate difficulty.\n\n"
            f"Subject: {context.subject}\n"
            f"Chapter: {context.chapter}\n"
            f"Topic: {context.topic}\n\n"
            "Textbook material:\n"
            f"{context.text}"
        )

    @staticmethod
    def _parse_response(
        response: Any,
        context: GenerationContext,
    ) -> list[Question]:
        if not hasattr(response, "text"):
            raise ValueError(
                "response does not contain text"
            )

        output_text = response.text

        if not isinstance(output_text, str) or not output_text.strip():
            raise ValueError(
                "response text must be non-empty"
            )

        try:
            data = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "response text contains invalid JSON"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "response JSON must be an object"
            )

        raw_questions = data.get("questions")

        if not isinstance(raw_questions, list):
            raise ValueError(
                "response JSON must contain a questions list"
            )

        questions: list[Question] = []

        for item in raw_questions:
            if not isinstance(item, dict):
                raise ValueError(
                    "each question must be a JSON object"
                )

            try:
                question = Question(
                    question=item["question"],
                    options=item["options"],
                    correct_answer=item["correct_answer"],
                    explanation=item["explanation"],
                    difficulty=item["difficulty"],
                    subject=context.subject,
                    chapter=context.chapter,
                    topic=context.topic,
                    source=context.source,
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    "invalid question data in response"
                ) from exc

            questions.append(question)

        return questions