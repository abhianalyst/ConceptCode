from collections.abc import Callable

from question_generator.generation.base import QuestionGenerator
from question_generator.generation.context import GenerationContext
from question_generator.schemas import Question


class LLMQuestionGenerator(QuestionGenerator):
    """
    Question generator backed by an injected LLM callable.

    The LLM integration is deliberately injected so the generation
    layer does not depend on a specific provider.
    """

    def __init__(
        self,
        generate_fn: Callable[[GenerationContext], list[Question]],
    ) -> None:
        if not callable(generate_fn):
            raise TypeError("generate_fn must be callable")

        self.generate_fn = generate_fn

    def generate(
        self,
        context: GenerationContext,
    ) -> list[Question]:
        if not isinstance(context, GenerationContext):
            raise TypeError(
                "context must be a GenerationContext"
            )

        questions = self.generate_fn(context)

        if not isinstance(questions, list):
            raise TypeError(
                "generate_fn must return a list"
            )

        if any(
            not isinstance(question, Question)
            for question in questions
        ):
            raise TypeError(
                "generate_fn must return only Question objects"
            )

        return questions