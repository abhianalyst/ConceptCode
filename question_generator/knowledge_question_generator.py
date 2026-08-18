from question_generator.basic_generator import (
    generate_definition_question,
)
from question_generator.concept_extractor import Concept
from question_generator.distractor_generator import (
    generate_concept_distractors,
)
from question_generator.knowledge_extractor import KnowledgeSet
from question_generator.question_schema import Question


def generate_question_from_concept(
    concept: Concept,
    *,
    knowledge_sets: tuple[KnowledgeSet, ...],
    subject: str,
    chapter: str,
    topic: str,
    source: str,
) -> Question:

    distractors = generate_concept_distractors(
        concept,
        knowledge_sets,
    )

    return generate_definition_question(
        subject=subject,
        chapter=chapter,
        topic=topic,
        definition=f"What is a {concept.name}?",
        correct_answer=concept.statement,
        distractors=distractors,
        explanation=concept.statement,
        source=source,
    )