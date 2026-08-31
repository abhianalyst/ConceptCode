from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Question:
    question: str
    options: list[str]
    correct_answer: str
    explanation: str
    difficulty: str
    subject: str
    chapter: str
    topic: str
    source: str
    year_tag: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("question must be a non-empty string")

        if len(self.options) != 4:
            raise ValueError("options must contain exactly 4 items")

        if any(
            not isinstance(option, str) or not option.strip()
            for option in self.options
        ):
            raise ValueError("all options must be non-empty strings")

        if self.correct_answer not in self.options:
            raise ValueError(
                "correct_answer must match one of the options"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "subject": self.subject,
            "chapter": self.chapter,
            "topic": self.topic,
            "source": self.source,
            "year_tag": self.year_tag,
        }