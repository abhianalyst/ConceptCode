from question_generator.question_quality import (
    is_duplicate_question,
    validate_question_quality,
)
from question_generator.question_schema import Question


def accept_question(
    question: Question,
    existing_questions: tuple[Question, ...],
) -> None:
    errors = validate_question_quality(
        question
    )

    if errors:
        raise ValueError(
            "Question failed quality checks: "
            + "; ".join(errors)
        )

    if is_duplicate_question(
        question,
        existing_questions,
    ):
        raise ValueError(
            "Question is a duplicate."
        )