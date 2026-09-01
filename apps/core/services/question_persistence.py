from question_generator.schemas import Question as GeneratedQuestion

from apps.core.models import (
    Chapter,
    Question,
    Subject,
    Topic,
)


def save_generated_question(
    generated_question: GeneratedQuestion,
) -> Question:
    """
    Persist a generated Question schema into the Django database.
    """

    if not isinstance(
        generated_question,
        GeneratedQuestion,
    ):
        raise TypeError(
            "generated_question must be a Question"
        )

    subject, _ = Subject.objects.get_or_create(
        name=generated_question.subject,
    )

    chapter, _ = Chapter.objects.get_or_create(
        subject=subject,
        name=generated_question.chapter,
        defaults={
            "unit_number": 0,
        },
    )

    topic, _ = Topic.objects.get_or_create(
        chapter=chapter,
        name=generated_question.topic,
    )

    return Question.objects.create(
        topic=topic,
        question=generated_question.question,
        option_a=generated_question.options[0],
        option_b=generated_question.options[1],
        option_c=generated_question.options[2],
        option_d=generated_question.options[3],
        correct_answer=generated_question.correct_answer,
        explanation=generated_question.explanation,
        difficulty=generated_question.difficulty,
        source=generated_question.source,
        year_tag=generated_question.year_tag,
    )