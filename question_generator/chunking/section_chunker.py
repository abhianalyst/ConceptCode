from question_generator.chunking.chunker import Chunk
from question_generator.schemas import Section


def chunk_section(
    section: Section,
    *,
    chunk_size: int = 2000,
    overlap: int = 200,
) -> list[Chunk]:
    """
    Split a Section into chunks while preserving section metadata.

    Chunks never lose their originating chapter or section context.
    """

    if not isinstance(section, Section):
        raise TypeError("section must be a Section")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0:
        raise ValueError("overlap must not be negative")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    text = section.text.strip()

    if not text:
        return []

    chunks: list[Chunk] = []

    start = 0

    while start < len(text):
        remaining = text[start:]

        if len(remaining) <= chunk_size:
            chunk_text = remaining.strip()
        else:
            end = start + chunk_size

            boundary = text.rfind("\n\n", start, end)

            if boundary > start:
                end = boundary

            chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                Chunk(
                    chunk_id=(
                        f"{section.source}-"
                        f"{section.number}-"
                        f"{len(chunks) + 1}"
                    ),
                    text=chunk_text,
                    source=section.source,
                    page_start=section.page_start,
                    page_end=section.page_end,
                    subject=section.subject,
                    chapter=section.chapter,
                    topic=section.title,
                )
            )

        if len(remaining) <= chunk_size:
            break

        start = max(
            start + 1,
            start + chunk_size - overlap,
        )

    return chunks