import re
from dataclasses import dataclass


@dataclass
class Concept:
    name: str
    statement: str
    source_text: str


def create_concept(
    name: str,
    statement: str,
    source_text: str,
) -> Concept:
    return Concept(
        name=name,
        statement=statement,
        source_text=source_text,
    )

def extract_concepts(text: str) -> list[Concept]:
    if not text.strip():
        raise ValueError(
            "Cannot extract concepts from empty text."
        )

    concepts = []

    pattern = re.compile(
        r"(?P<definition>"
        r"(?P<subject>(?:An|A|The)\s+"
        r"[A-Za-z][^.!?]{2,100}?)"
        r"\s+"
        r"(?:is called|is known as|is defined as)\s+"
        r"(?P<name>[A-Za-z][^.!?]{1,100}?)"
        r"\.)",
        re.IGNORECASE,
    )

    for match in pattern.finditer(text):
        definition = _normalize_statement(
                    match.group("definition")
                    )
        name = re.sub(
                        r"^(?:a|an|the)\s+",
                        "",
                        _normalize_statement(match.group("name")),
                        flags=re.IGNORECASE,
                    )

        concepts.append(
            create_concept(
                name=name,
                statement=definition,
                source_text=definition,
            )
        )

    return concepts

def _normalize_statement(text: str) -> str:
    return " ".join(text.split())

def _is_definition_sentence(sentence: str) -> bool:
    lowered = sentence.lower()

    return (
        " is defined as " in lowered
        or " is known as " in lowered
        or " is called " in lowered
    )