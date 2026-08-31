from dataclasses import dataclass
from typing import Any

from question_generator.schemas.document import Document


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    source: str
    page_start: int | None = None
    page_end: int | None = None
    subject: str | None = None
    chapter: str | None = None
    topic: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source": self.source,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "subject": self.subject,
            "chapter": self.chapter,
            "topic": self.topic,
        }


def chunk_text(
    text: str,
    *,
    chunk_size: int = 2000,
    overlap: int = 200,
    source: str = "",
    page_start: int | None = None,
    page_end: int | None = None,
    subject: str | None = None,
    chapter: str | None = None,
    topic: str | None = None,
) -> list[Chunk]:
    """
    Split text into overlapping, paragraph-aware chunks.

    chunk_size and overlap are measured in characters.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0:
        raise ValueError("overlap must not be negative")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    text = text.strip()

    if not text:
        return []

    chunks: list[Chunk] = []

    def make_chunk(value: str) -> Chunk:
        return Chunk(
            chunk_id=f"chunk-{len(chunks) + 1}",
            text=value,
            source=source,
            page_start=page_start,
            page_end=page_end,
            subject=subject,
            chapter=chapter,
            topic=topic,
        )

    start = 0
    text_length = len(text)

    while start < text_length:
        remaining = text[start:]

        if len(remaining) <= chunk_size:
            chunks.append(make_chunk(remaining))
            break

        end = start + chunk_size

        # Prefer the last paragraph boundary inside the chunk.
        boundary = text.rfind("\n\n", start, end)

        if boundary > start:
            end = boundary

        chunk_value = text[start:end].strip()

        if chunk_value:
            chunks.append(make_chunk(chunk_value))

        # Prevent an infinite loop if no usable text was produced.
        if end <= start:
            end = min(start + chunk_size, text_length)

        # Move forward while retaining overlap.
        start = max(end - overlap, start + 1)

    return chunks

def chunk_document(
    document: Document,
    *,
    chunk_size: int = 2000,
    overlap: int = 200,
    subject: str | None = None,
    chapter: str | None = None,
    topic: str | None = None,
) -> list[Chunk]:
    """
    Chunk all pages in a Document while preserving page metadata.

    Each page is chunked independently so a chunk never silently
    crosses a PDF page boundary.
    """

    if not isinstance(document, Document):
        raise TypeError("document must be a Document")

    chunks: list[Chunk] = []

    for page in document.pages:
        page_chunks = chunk_text(
            page.text,
            chunk_size=chunk_size,
            overlap=overlap,
            source=document.filename,
            page_start=page.page_number,
            page_end=page.page_number,
            subject=subject,
            chapter=chapter,
            topic=topic,
        )

        for chunk in page_chunks:
            chunk_number = len(chunks) + 1

            chunks.append(
                Chunk(
                    chunk_id=f"{document.filename}-{chunk_number}",
                    text=chunk.text,
                    source=chunk.source,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    subject=chunk.subject,
                    chapter=chunk.chapter,
                    topic=chunk.topic,
                )
            )

    return chunks


def chunk_documents(
    documents: list[Document],
    *,
    chunk_size: int = 2000,
    overlap: int = 200,
    subject: str | None = None,
    chapter: str | None = None,
    topic: str | None = None,
) -> list[Chunk]:
    """
    Chunk all pages in a list of Documents while preserving page metadata.

    Each page is chunked independently so a chunk never silently
    crosses a PDF page boundary.
    """

    if not isinstance(documents, list):
        raise TypeError("documents must be a list of Document")

    chunks: list[Chunk] = []

    for document in documents:
        document_chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            overlap=overlap,
            subject=subject,
            chapter=chapter,
            topic=topic,
        )

        chunks.extend(document_chunks)

    return chunks