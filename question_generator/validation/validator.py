from question_generator.schemas import Question


VALID_DIFFICULTIES = {
    "Easy",
    "Medium",
    "Hard",
}


def validate_question(question: Question) -> Question:
    """Validate a generated Question and return it unchanged."""

    if not isinstance(question, Question):
        raise TypeError("question must be a Question")

    if len(set(question.options)) != 4:
        raise ValueError("options must be unique")

    if question.correct_answer not in question.options:
        raise ValueError(
            "correct_answer must match one of the options"
        )

    if not question.explanation.strip():
        raise ValueError("explanation must be non-empty")

    if question.difficulty not in VALID_DIFFICULTIES:
        raise ValueError(
            "difficulty must be Easy, Medium, or Hard"
        )

    for field_name in (
        "subject",
        "chapter",
        "topic",
        "source",
    ):
        value = getattr(question, field_name)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must be non-empty"
            )

    return question