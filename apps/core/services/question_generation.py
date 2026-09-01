from apps.core.models import Topic
from apps.core.services.llm_provider import (
    get_gemini_question_provider,
)
from question_generator.generation import (
    QuestionGenerationService,
    build_generation_context,
)
from question_generator.generation.llm import (
    LLMQuestionGenerator,
)
from question_generator.persistence import save_questions
from question_generator.schemas import Section


def get_question_generation_service() -> QuestionGenerationService:
    """Build the production question-generation service."""

    provider = get_gemini_question_provider()

    generator = LLMQuestionGenerator(
        provider.generate,
    )

    return QuestionGenerationService(
        generator,
    )


def generate_questions_for_section(
    section: Section,
    *,
    topic: Topic,
    service: QuestionGenerationService | None = None,
):
    """
    Generate, validate, deduplicate, and persist questions
    for one textbook section.

    If no service is supplied, the production Gemini-backed
    service is created automatically.
    """

    if not isinstance(section, Section):
        raise TypeError("section must be a Section")

    if not isinstance(topic, Topic):
        raise TypeError("topic must be a Topic")

    if service is None:
        service = get_question_generation_service()

    if not isinstance(
        service,
        QuestionGenerationService,
    ):
        raise TypeError(
            "service must be a QuestionGenerationService"
        )

    context = build_generation_context(
        section,
        subject=section.subject or "",
        source=section.source,
    )

    questions = service.generate(context)

    return save_questions(
        questions,
        topic=topic,
    )