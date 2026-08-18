from question_generator.concept_extractor import Concept
from question_generator.knowledge_extractor import KnowledgeSet


def collect_concept_candidates(
    knowledge_sets: tuple[KnowledgeSet, ...],
) -> tuple[Concept, ...]:
    candidates = []

    for knowledge in knowledge_sets:
        candidates.extend(knowledge.concepts)

    return tuple(candidates)


def generate_concept_distractors(
    concept: Concept,
    knowledge_sets: tuple[KnowledgeSet, ...],
) -> tuple[str, str, str]:
    candidates = collect_concept_candidates(
        knowledge_sets
    )

    distractors = []

    for candidate in candidates:
        if candidate == concept:
            continue

        if candidate.statement == concept.statement:
            continue

        if candidate.statement in distractors:
            continue

        distractors.append(candidate.statement)

        if len(distractors) == 3:
            break

    if len(distractors) < 3:
        raise ValueError(
            "Not enough concept candidates available "
            "to generate three distractors."
        )

    result = tuple(distractors)

    errors = validate_distractors(
        concept.statement,
        result,
    )

    if errors:
        raise ValueError(
            "Invalid distractors: "
            + "; ".join(errors)
        )

    return result

def _normalize_option(text: str) -> str:
    return " ".join(text.split()).strip().lower()


def validate_distractors(
    correct_answer: str,
    distractors: tuple[str, str, str],
) -> list[str]:
    errors = []

    if len(distractors) != 3:
        errors.append(
            "Exactly three distractors are required."
        )
        return errors

    normalized_correct = _normalize_option(
        correct_answer
    )

    normalized_distractors = [
        _normalize_option(distractor)
        for distractor in distractors
    ]

    if any(not distractor for distractor in normalized_distractors):
        errors.append(
            "Distractors cannot be empty."
        )

    if len(set(normalized_distractors)) != 3:
        errors.append(
            "Distractors must be unique."
        )

    if normalized_correct in normalized_distractors:
        errors.append(
            "A distractor cannot equal the correct answer."
        )

    return errors