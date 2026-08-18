from dataclasses import dataclass

from question_generator.chunker import TextChunk
from question_generator.concept_extractor import (
    Concept,
    extract_concepts,
)
from question_generator.fact_extractor import (
    Fact,
    extract_facts,
)


@dataclass(frozen=True)
class KnowledgeSet:
    subject: str
    chapter: str
    topic: str
    concepts: tuple[Concept, ...]
    facts: tuple[Fact, ...]


def extract_knowledge(
    chunk: TextChunk,
) -> KnowledgeSet:
    concepts = tuple(
        extract_concepts(chunk.text)
    )

    facts = tuple(
        extract_facts(chunk.text)
    )

    return KnowledgeSet(
        subject=chunk.subject,
        chapter=chunk.chapter,
        topic=chunk.topic,
        concepts=concepts,
        facts=facts,
    )