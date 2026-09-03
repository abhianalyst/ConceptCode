from collections.abc import Callable

from question_generator.generation.base import QuestionGenerator
from question_generator.generation.context import GenerationContext
from question_generator.schemas import Question


class LLMQuestionGenerator(QuestionGenerator):
    """Question generator backed by an injected LLM callable."""

    def __init__(self, generate_fn: Callable[..., list[Question]]) -> None:
        if not callable(generate_fn):
            raise TypeError("generate_fn must be callable")

        self.generate_fn = generate_fn

    def generate(
        self,
        context: GenerationContext,
        *,
        difficulty: str | None = None,
    ) -> list[Question]:
        if not isinstance(context, GenerationContext):
            raise TypeError("context must be a GenerationContext")

        if difficulty is None:
            questions = self.generate_fn(context)
        else:
            questions = self.generate_fn(
                context,
                difficulty=difficulty,
            )

        if not isinstance(questions, list):
            raise TypeError("generate_fn must return a list")

        if any(
            not isinstance(question, Question)
            for question in questions
        ):
            raise TypeError(
                "generate_fn must return only Question objects"
            )

        return questions