
from question_generator.generation.base import QuestionGenerator
from question_generator.generation.context import GenerationContext
from question_generator.schemas import Question
from question_generator.validation.duplicate import filter_duplicates
from question_generator.validation.validator import validate_question


class QuestionGenerationService:
    """Generate, validate, and deduplicate questions."""

    def __init__(
        self,
        generator: QuestionGenerator,
    ) -> None:
        if not isinstance(generator, QuestionGenerator):
            raise TypeError(
                "generator must be a QuestionGenerator"
            )

        self.generator = generator

    def generate(
        self,
        context: GenerationContext,
    ) -> list[Question]:
        if not isinstance(context, GenerationContext):
            raise TypeError(
                "context must be a GenerationContext"
            )

        questions = self.generator.generate(context)

        validated_questions: list[Question] = []

        for question in questions:
            validated_questions.append(
                validate_question(question)
            )

        return filter_duplicates(validated_questions)
