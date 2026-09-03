from collections import Counter

from question_generator.schemas import Question


DIFFICULTIES = (
    "Easy",
    "Medium",
    "Hard",
)

QUESTIONS_PER_DIFFICULTY = 20
TOTAL_QUESTIONS_PER_TOPIC = 60


def count_by_difficulty(
    questions: list[Question],
) -> dict[str, int]:
    """Count generated questions by difficulty."""

    if not isinstance(questions, list):
        raise TypeError("questions must be a list")

    if any(
        not isinstance(question, Question)
        for question in questions
    ):
        raise TypeError(
            "questions must contain only Question objects"
        )

    counts = Counter(
        question.difficulty
        for question in questions
    )

    return {
        difficulty: counts.get(difficulty, 0)
        for difficulty in DIFFICULTIES
    }


def is_target_reached(
    questions: list[Question],
) -> bool:
    """Return True when a topic has exactly the required distribution."""

    counts = count_by_difficulty(questions)

    return all(
        counts[difficulty] >= QUESTIONS_PER_DIFFICULTY
        for difficulty in DIFFICULTIES
    )
