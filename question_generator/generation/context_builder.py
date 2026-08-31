from question_generator.chunking import chunk_section
from question_generator.generation.context import GenerationContext
from question_generator.schemas import Section


def build_generation_context(
    section: Section,
    *,
    subject: str,
    source: str,
    chunk_size: int = 2000,
    overlap: int = 200,
) -> GenerationContext:
    """
    Convert a textbook Section into a GenerationContext.
    """

    if not isinstance(section, Section):
        raise TypeError("section must be a Section")

    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("subject must be a non-empty string")

    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")

    chunks = chunk_section(
        section,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if not chunks:
        raise ValueError(
            f"Section contains no usable text: "
            f"{section.number} {section.title}"
        )

    return GenerationContext(
        subject=subject,
        chapter=section.chapter or "",
        topic=section.title,
        source=source,
        chunks=chunks,
    )
