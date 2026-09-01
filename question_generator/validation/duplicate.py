import hashlib
import re

from question_generator.schemas import Question


def normalize_question_text(text: str) -> str:
    """Normalize question text for duplicate detection."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip().lower()

    return re.sub(r"\s+", " ", text)


def fingerprint_text(text: str) -> str:
    """Return a stable SHA-256 fingerprint for question text."""

    normalized = normalize_question_text(text)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def question_fingerprint(question: Question) -> str:
    """Return a stable SHA-256 fingerprint for a Question."""

    if not isinstance(question, Question):
        raise TypeError("question must be a Question")

    return fingerprint_text(question.question)


def filter_duplicates(
    questions: list[Question],
) -> list[Question]:
    """Return questions with duplicate question text removed."""

    if not isinstance(questions, list):
        raise TypeError("questions must be a list")

    unique_questions: list[Question] = []
    fingerprints: set[str] = set()

    for question in questions:
        if not isinstance(question, Question):
            raise TypeError(
                "questions must contain only Question objects"
            )

        fingerprint = question_fingerprint(question)

        if fingerprint in fingerprints:
            continue

        fingerprints.add(fingerprint)
        unique_questions.append(question)

    return unique_questions