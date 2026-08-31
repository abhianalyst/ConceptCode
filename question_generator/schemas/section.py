from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Section:
    """A textbook section containing its source content."""

    section_id: str
    number: str
    title: str
    text: str
    source: str
    page_start: int
    page_end: int
    subject: str | None = None
    chapter: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "number": self.number,
            "title": self.title,
            "text": self.text,
            "source": self.source,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "subject": self.subject,
            "chapter": self.chapter,
        }