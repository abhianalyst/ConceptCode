from question_generator.generation.context import GenerationContext
from question_generator.generation.service import QuestionGenerationService
from question_generator.generation.target import (
    DIFFICULTIES,
    QUESTIONS_PER_DIFFICULTY,
)
from question_generator.schemas import Question
from question_generator.validation.duplicate import filter_duplicates


MAX_BATCH_ATTEMPTS = 10


def generate_questions_for_topic(
    context: GenerationContext,
    service: QuestionGenerationService,
) -> list[Question]:
    if not isinstance(context, GenerationContext):
        raise TypeError("context must be a GenerationContext")

    if not isinstance(service, QuestionGenerationService):
        raise TypeError(
            "service must be a QuestionGenerationService"
        )

    generated: list[Question] = []

    for difficulty in DIFFICULTIES:
        difficulty_questions: list[Question] = []

        for _ in range(MAX_BATCH_ATTEMPTS):
            remaining = (
                QUESTIONS_PER_DIFFICULTY
                - len(difficulty_questions)
            )

            if remaining <= 0:
                break

            batch = service.generate(
                context,
                difficulty=difficulty,
            )

            batch = [
                question
                for question in batch
                if question.difficulty == difficulty
            ]

            difficulty_questions.extend(batch)

            difficulty_questions = filter_duplicates(
                difficulty_questions
            )

        if len(difficulty_questions) < QUESTIONS_PER_DIFFICULTY:
            raise ValueError(
                f"Could not generate "
                f"{QUESTIONS_PER_DIFFICULTY} "
                f"{difficulty} questions for topic "
                f"{context.topic!r}"
            )

        generated.extend(
            difficulty_questions[:QUESTIONS_PER_DIFFICULTY]
        )

    return generated