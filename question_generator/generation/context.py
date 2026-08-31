from dataclasses import dataclass

from question_generator.chunking import Chunk


@dataclass(frozen=True)
class GenerationContext:
    """Chapter/topic context supplied to a question generator."""

    subject: str
    chapter: str
    topic: str
    source: str
    chunks: list[Chunk]

    def __post_init__(self) -> None:
        if not isinstance(self.subject, str) or not self.subject.strip():
            raise ValueError("subject must be a non-empty string")

        if not isinstance(self.chapter, str) or not self.chapter.strip():
            raise ValueError("chapter must be a non-empty string")

        if not isinstance(self.topic, str) or not self.topic.strip():
            raise ValueError("topic must be a non-empty string")

        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")

        if not isinstance(self.chunks, list):
            raise TypeError("chunks must be a list")

        if not self.chunks:
            raise ValueError("chunks must contain at least one Chunk")

        if any(not isinstance(chunk, Chunk) for chunk in self.chunks):
            raise TypeError("chunks must contain only Chunk objects")

    @property
    def text(self) -> str:
        """Return the chapter/topic content represented by the chunks."""
        return "\n\n".join(chunk.text for chunk in self.chunks)
