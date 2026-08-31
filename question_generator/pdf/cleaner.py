import re


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving its meaning.

    The cleaner:
    - normalizes line endings
    - removes excessive whitespace
    - removes excessive blank lines
    - strips leading/trailing whitespace

    It does not attempt to detect chapters, topics, or headings.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    # Normalize Windows/Mac line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize tabs and other horizontal whitespace.
    text = re.sub(r"[^\S\n]+", " ", text)

    # Remove spaces immediately before/after line breaks.
    text = re.sub(r" *\n *", "\n", text)

    # Collapse 3+ consecutive blank lines into 2.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()