import re


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving paragraph boundaries.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_page_artifacts(text: str) -> str:
    """
    Remove common PDF extraction artifacts without
    aggressively modifying textbook content.
    """
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            lines.append("")
            continue

        if re.fullmatch(r"\d+", line):
            continue

        if re.fullmatch(r"[A-Z]\s+[A-Z]", line):
            continue

        lines.append(line)

    return "\n".join(lines)


def preprocess_text(text: str) -> str:
    """
    Convert extracted PDF text into cleaner source text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if not text.strip():
        return ""

    text = remove_page_artifacts(text)
    text = normalize_whitespace(text)

    return text