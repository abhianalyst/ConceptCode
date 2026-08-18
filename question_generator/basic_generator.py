from question_generator.question_schema import (
    Difficulty,
    Question,
)


def generate_definition_question(
    *,
    subject: str,
    chapter: str,
    topic: str,
    definition: str,
    correct_answer: str,
    distractors: tuple[str, str, str],
    explanation: str,
    source: str,
) -> Question:

    options = (
        correct_answer,
        *distractors,
    )

    return Question(
        question=definition,
        options=options,
        correct_answer=correct_answer,
        explanation=explanation,
        difficulty=Difficulty.EASY,
        subject=subject,
        chapter=chapter,
        topic=topic,
        source=source,
    )

def generate_from_chunk(
    chunk,
    *,
    question: str,
    correct_answer: str,
    distractors: tuple[str, str, str],
    explanation: str,
) -> Question:
    return generate_definition_question(
        subject=chunk.subject,
        chapter=chunk.chapter,
        topic=chunk.topic,
        definition=question,
        correct_answer=correct_answer,
        distractors=distractors,
        explanation=explanation,
        source="NCERT",
    )