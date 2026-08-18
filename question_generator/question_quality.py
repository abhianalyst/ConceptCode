import re

from question_generator.question_schema import Question
from question_generator.question_validator import validate_question


def _normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def is_duplicate_question(
    question: Question,
    existing_questions: tuple[Question, ...],
) -> bool:
    normalized = _normalize_text(
        question.question
    )

    return any(
        normalized == _normalize_text(
            existing.question
        )
        for existing in existing_questions
    )


def validate_question_quality(
    question: Question,
) -> list[str]:
    errors = list(
        validate_question(question)
    )

    if len(question.question.strip()) < 10:
        errors.append(
            "Question text is too short."
        )

    return errors