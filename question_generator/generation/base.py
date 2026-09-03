from abc import ABC, abstractmethod

from question_generator.generation.context import GenerationContext
from question_generator.schemas import Question


class QuestionGenerator(ABC):
    """Abstract interface for chapter-aware question generation."""

    @abstractmethod
    def generate(
        self,
        context: GenerationContext,
        *,
        difficulty: str | None = None,
    ) -> list[Question]:
        """
        Generate questions from a chapter/topic generation context.

        Args:
            context: Chapter/topic content supplied for generation.
            difficulty: Optional requested difficulty.

        Returns:
            A list of generated Question objects.
        """
        raise NotImplementedError