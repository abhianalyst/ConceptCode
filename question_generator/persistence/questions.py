from django.db import IntegrityError

from apps.core.models import Question as QuestionModel
from question_generator.schemas import Question
from question_generator.validation.duplicate import (
    question_fingerprint,
)

from django.db import transaction

def save_question(
    question: Question,
    *,
    topic,
) -> QuestionModel:
    """Persist a validated Question schema to the Django database."""

    if not isinstance(question, Question):
        raise TypeError("question must be a Question")

    if topic is None:
        raise ValueError("topic is required")

    options = question.options
    fingerprint = question_fingerprint(question)

    try:
        return QuestionModel.objects.create(
            topic=topic,
            question=question.question,
            question_fingerprint=fingerprint,
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            difficulty=question.difficulty,
            source=question.source,
            year_tag=question.year_tag,
        )
    except IntegrityError as exc:
        raise ValueError(
            "question already exists"
        ) from exc


@transaction.atomic
def save_questions(
    questions: list[Question],
    *,
    topic,
) -> list[QuestionModel]:
    """Persist a validated batch of questions atomically."""

    if not isinstance(questions, list):
        raise TypeError("questions must be a list")

    saved_questions: list[QuestionModel] = []

    for question in questions:
        saved_questions.append(
            save_question(
                question,
                topic=topic,
            )
        )

    return saved_questions