from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Fact:
    statement: str
    source_text: str


def create_fact(
    statement: str,
    source_text: str,
) -> Fact:
    return Fact(
        statement=statement.strip(),
        source_text=source_text.strip(),
    )


def extract_facts(text: str) -> list[Fact]:
    if not text.strip():
        raise ValueError(
            "Cannot extract facts from empty text."
        )

    return []

def _normalize_statement(text: str) -> str:
    return " ".join(text.split())


def extract_facts(text: str) -> list[Fact]:
    if not text.strip():
        raise ValueError(
            "Cannot extract facts from empty text."
        )

    facts = []

    pattern = re.compile(
        r"(?P<statement>"
        r"(?P<term>[A-Za-z][A-Za-z0-9_()]*)"
        r"\s+is known as\s+"
        r"(?P<meaning>[^.?!]{2,150})"
        r"\.)",
        re.IGNORECASE,
    )

    for match in pattern.finditer(text):
        statement = _normalize_statement(
            match.group("statement")
        )

        facts.append(
            create_fact(
                statement=statement,
                source_text=statement,
            )
        )

    return facts