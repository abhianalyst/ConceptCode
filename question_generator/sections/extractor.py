import re

from question_generator.schemas import Section


SECTION_HEADING_PATTERN = re.compile(
    r"^\s*(\d+\.\d+)\s+(.+?)\s*$",
    re.IGNORECASE,
)

# The real section headings in the NCERT Biology chapter are
# uppercase. TOC entries use normal title case.
def _is_real_section_heading(line: str) -> bool:
    match = SECTION_HEADING_PATTERN.match(line)

    if not match:
        return False

    title = match.group(2).strip()

    return title == title.upper()


def extract_sections(
    pages: list[dict],
    *,
    source: str,
    chapter: str,
    subject: str | None = None,
) -> list[Section]:
    """
    Extract real numbered sections from an already-isolated chapter.

    Section headings are identified from PDF blocks. Normal title-case
    table-of-contents entries are ignored.
    """

    if not isinstance(pages, list):
        raise TypeError("pages must be a list")

    if not pages:
        return []

    sections: list[Section] = []

    current_number: str | None = None
    current_title: str | None = None
    current_page_start: int | None = None
    current_page_end: int | None = None
    current_text: list[str] = []

    def save_current_section() -> None:
        if (
            current_number is None
            or current_title is None
            or current_page_start is None
            or current_page_end is None
        ):
            return

        text = "\n\n".join(
            value.strip()
            for value in current_text
            if value.strip()
        ).strip()

        if not text:
            return

        sections.append(
            Section(
                section_id=f"{source}-{chapter}-{current_number}",
                number=current_number,
                title=current_title,
                text=text,
                source=source,
                page_start=current_page_start,
                page_end=current_page_end,
                subject=subject,
                chapter=chapter,
            )
        )

    for page in pages:
        page_number = page.get("page_number")

        if not isinstance(page_number, int):
            continue

        for block in page.get("blocks", []):
            block_text = block.get("text", "").strip()

            if not block_text:
                continue

            for line in block_text.splitlines():
                line = line.strip()

                if not line:
                    continue

                match = SECTION_HEADING_PATTERN.match(line)

                if match and _is_real_section_heading(line):
                    save_current_section()

                    current_number = match.group(1)
                    current_title = match.group(2).strip()
                    current_page_start = page_number
                    current_page_end = page_number
                    current_text = []

                    continue

                if current_number is not None:
                    current_text.append(line)
                    current_page_end = page_number

    save_current_section()

    return sections