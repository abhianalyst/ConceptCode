import json
import random
import time
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


MAX_RETRIES = 4
INITIAL_BACKOFF_SECONDS = 2.0
MAX_BACKOFF_SECONDS = 30.0


class GeminiQuestionProvider:
    """Generate questions using Google's Gemini API."""

    def __init__(self, client: Any, *, model: str) -> None:
        if client is None:
            raise ValueError("client is required")

        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a non-empty string")

        self.client = client
        self.model = model

    def generate(
        self,
        context: GenerationContext,
        *,
        difficulty: str | None = None,
    ) -> list[Question]:
        if not isinstance(context, GenerationContext):
            raise TypeError("context must be a GenerationContext")

        if difficulty is not None:
            if not isinstance(difficulty, str) or not difficulty.strip():
                raise ValueError("difficulty must be a non-empty string")

            difficulty = difficulty.strip()

        prompt = self._build_prompt(
            context,
            difficulty=difficulty,
        )

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QUESTION_SCHEMA,
        )

        response = self._generate_with_retry(
            prompt=prompt,
            config=config,
        )

        return self._parse_response(
            response,
            context,
        )

    def _generate_with_retry(
        self,
        *,
        prompt: str,
        config: Any,
    ) -> Any:
        delay = INITIAL_BACKOFF_SECONDS

        for attempt in range(MAX_RETRIES + 1):
            try:
                return self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )

            except Exception as exc:
                if self._is_quota_exhausted_error(exc):
                    raise RuntimeError(
                        "Gemini API quota exhausted. "
                        "The free-tier request quota has been reached. "
                        "Wait for the quota reset or use a project/model "
                        "with available quota."
                    ) from exc

                if not self._is_retryable_error(exc):
                    raise

                if attempt >= MAX_RETRIES:
                    raise RuntimeError(
                        "Gemini API request failed after "
                        f"{MAX_RETRIES + 1} attempts."
                    ) from exc

                sleep_seconds = min(
                    delay,
                    MAX_BACKOFF_SECONDS,
                )

                sleep_seconds *= random.uniform(0.8, 1.2)

                time.sleep(sleep_seconds)

                delay = min(
                    delay * 2,
                    MAX_BACKOFF_SECONDS,
                )

        raise RuntimeError("Gemini API request failed.")

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        message = str(exc).upper()

        return (
            "503" in message
            or "UNAVAILABLE" in message
            or "SERVICE UNAVAILABLE" in message
        )

    @staticmethod
    def _is_quota_exhausted_error(exc: Exception) -> bool:
        message = str(exc).upper()

        return (
            "429" in message
            or "RESOURCE_EXHAUSTED" in message
            or "QUOTA EXCEEDED" in message
            or "GENERATEREQUESTSPERDAYPERPROJECT-FREETIER" in message
        )

    @staticmethod
    def _build_prompt(
        context: GenerationContext,
        *,
        difficulty: str | None = None,
    ) -> str:
        prompt = (
            "Generate multiple-choice questions using only the "
            "provided textbook material.\n\n"
            "Rules:\n"
            "- Use only information supported by the textbook material.\n"
            "- Generate high-quality multiple-choice questions.\n"
            "- Every question must have exactly 4 options.\n"
            "- correct_answer must exactly match one option.\n"
            "- Include a concise explanation.\n"
        )

        if difficulty is None:
            prompt += (
                "- Assign an appropriate difficulty to every question.\n"
            )
        else:
            prompt += (
                f"- Every question must have difficulty: {difficulty}.\n"
                "- Generate exactly 20 questions.\n"
            )

        prompt += (
            "\n"
            f"Subject: {context.subject}\n"
            f"Chapter: {context.chapter}\n"
            f"Topic: {context.topic}\n\n"
            "Textbook material:\n"
            f"{context.text}"
        )

        return prompt

    @staticmethod
    def _parse_response(
        response: Any,
        context: GenerationContext,
    ) -> list[Question]:
        if not hasattr(response, "text"):
            raise ValueError("response does not contain text")

        output_text = response.text

        if not isinstance(output_text, str) or not output_text.strip():
            raise ValueError("response text must be non-empty")

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