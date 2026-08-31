import json
from typing import Any

from question_generator.generation.context import GenerationContext
from question_generator.schemas import Question


class OpenAIQuestionProvider:
    """
    Provider adapter for OpenAI-backed question generation.

    The OpenAI client is injected so this class can be tested
    without making real API requests.
    """

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

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return self._parse_response(response, context)

    @staticmethod
    def _build_prompt(
        context: GenerationContext,
    ) -> str:
        return (
            "Generate multiple-choice questions using only the "
            "provided textbook material.\n\n"
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
        if not hasattr(response, "output_text"):
            raise NotImplementedError(
                "Structured response parsing requires output_text."
            )

        output_text = response.output_text

        if not isinstance(output_text, str) or not output_text.strip():
            raise ValueError(
                "response output_text must be non-empty"
            )

        try:
            data = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "response output_text contains invalid JSON"
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
