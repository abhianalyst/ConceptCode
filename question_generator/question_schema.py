from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional


class Difficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass(frozen=True)
class Question:
    question: str
    options: tuple[str, str, str, str]
    correct_answer: str
    explanation: str
    difficulty: Difficulty
    subject: str
    chapter: str
    topic: str
    source: str
    year_tag: Optional[str] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["difficulty"] = self.difficulty.value
        data["options"] = list(self.options)
        return data