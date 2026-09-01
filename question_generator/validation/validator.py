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

    if not question.explanation.strip():
        raise ValueError("explanation must be non-empty")

    if question.difficulty not in VALID_DIFFICULTIES:
        raise ValueError(
            "difficulty must be Easy, Medium, or Hard"
        )

    return question