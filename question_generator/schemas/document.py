from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TextBlock:
    text: str
    bbox: tuple[float, float, float, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Page:
    page_number: int
    text: str
    blocks: list[TextBlock]

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "text": self.text,
            "blocks": [block.to_dict() for block in self.blocks],
        }


@dataclass(frozen=True)
class Document:
    filename: str
    title: str
    page_count: int
    pages: list[Page]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document": {
                "filename": self.filename,
                "title": self.title,
                "page_count": self.page_count,
            },
            "pages": [page.to_dict() for page in self.pages],
        }