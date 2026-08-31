from question_generator.generation.base import QuestionGenerator
from question_generator.generation.context import GenerationContext
from question_generator.schemas import Question


class MockQuestionGenerator(QuestionGenerator):
    """Deterministic content-aware generator for development and testing."""

    def __init__(self, questions_per_context: int = 1) -> None:
        if questions_per_context <= 0:
            raise ValueError(
                "questions_per_context must be greater than zero"
            )

        self.questions_per_context = questions_per_context

    def generate(
        self,
        context: GenerationContext,
    ) -> list[Question]:
        if not isinstance(context, GenerationContext):
            raise TypeError(
                "context must be a GenerationContext"
            )

        questions: list[Question] = []

        # Use the first non-empty sentence as deterministic
        # source material for the mock question.
        sentences = [
            sentence.strip()
            for sentence in context.text.replace("\n", " ").split(".")
            if sentence.strip()
        ]

        if not sentences:
            raise ValueError(
                "context contains no usable sentence content"
            )

        source_sentence = sentences[0]

        for index in range(
            1,
            self.questions_per_context + 1,
        ):
            questions.append(
                Question(
                    question=(
                        f"According to the chapter material, "
                        f"which statement is supported by the text? "
                        f"({index})"
                    ),
                    options=[
                        source_sentence,
                        "The text contains no information on this topic.",
                        "The chapter discusses an unrelated subject.",
                        "None of the above.",
                    ],
                    correct_answer=source_sentence,
                    explanation=(
                        "This answer is taken directly from the "
                        "chapter material supplied to the generator."
                    ),
                    difficulty="Easy",
                    subject=context.subject,
                    chapter=context.chapter,
                    topic=context.topic,
                    source=context.source,
                )
            )

        return questions