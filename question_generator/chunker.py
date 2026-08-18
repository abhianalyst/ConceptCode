from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    subject: str
    chapter: str
    topic: str
    text: str

def create_chunk(
    subject: str,
    chapter: str,
    topic: str,
    text: str,
) -> TextChunk:
    if not subject.strip():
        raise ValueError("subject cannot be empty")

    if not chapter.strip():
        raise ValueError("chapter cannot be empty")

    if not topic.strip():
        raise ValueError("topic cannot be empty")

    if not text.strip():
        raise ValueError("text cannot be empty")

    return TextChunk(
        subject=subject.strip(),
        chapter=chapter.strip(),
        topic=topic.strip(),
        text=text.strip(),
    )