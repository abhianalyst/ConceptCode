import logging

from question_generator.generation.context_builder import (
    build_generation_context,
)
from question_generator.generation.service import (
    QuestionGenerationService,
)
from question_generator.schemas import Question
from question_generator.validation.duplicate import (
    filter_duplicates,
)


logger = logging.getLogger(__name__)


def generate_questions_from_sections(
    sections,
    *,
    subject: str,
    source: str,
    service: QuestionGenerationService,
) -> list[Question]:
    """Generate validated, deduplicated questions from sections."""

    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("subject must be a non-empty string")

    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")

    if not isinstance(
        service,
        QuestionGenerationService,
    ):
        raise TypeError(
            "service must be a QuestionGenerationService"
        )

    logger.info(
        "Starting question generation: subject=%s source=%s sections=%s",
        subject,
        source,
        len(sections),
    )

    questions: list[Question] = []

    for index, section in enumerate(sections, start=1):
        logger.info(
            "Generating questions for section %s/%s: %s",
            index,
            len(sections),
            getattr(section, "title", "unknown"),
        )

        context = build_generation_context(
            section,
            subject=subject,
            source=source,
        )

        generated_questions = service.generate(context)

        logger.info(
            "Section %s generated %s questions",
            index,
            len(generated_questions),
        )

        questions.extend(generated_questions)

    before_deduplication = len(questions)

    questions = filter_duplicates(questions)

    duplicates_removed = (
        before_deduplication - len(questions)
    )

    logger.info(
        "Question generation complete: generated=%s "
        "duplicates_removed=%s final=%s",
        before_deduplication,
        duplicates_removed,
        len(questions),
    )

    return questions