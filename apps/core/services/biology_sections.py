import re
from dataclasses import dataclass

from apps.core.services.biology_source import get_chapter_pages


SECTION_PATTERN = re.compile(
    r"^\s*(\d+\.\d+)\s+(.+?)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BiologySection:
    """A numbered section within a Biology chapter."""

    section_number: str
    title: str
    start_page: int
    end_page: int
    text: str

    @property
    def topic(self) -> str:
        """Return the section title as the generation topic."""
        return self.title


def extract_sections(
    class_name: str,
    chapter_number: int,
) -> list[BiologySection]:
    """
    Extract the actual numbered sections from a Biology chapter.

    Contents-page entries are ignored. Section boundaries are
    determined from the actual section headings appearing in
    the chapter body.
    """

    pages = get_chapter_pages(
        class_name,
        chapter_number,
    )

    if not pages:
        return []

    candidates = []

    for page in pages:
        page_number = page["page_number"]

        for block in page.get("blocks", []):
            block_text = block.get("text", "")

            for line in block_text.splitlines():
                line = line.strip()

                match = SECTION_PATTERN.match(line)

                if not match:
                    continue

                section_number = match.group(1)
                title = match.group(2).strip()

                candidates.append(
                    {
                        "section_number": section_number,
                        "title": title,
                        "page_number": page_number,
                    }
                )

    # ---------------------------------------------------------
    # Keep only the actual section headings.
    #
    # The contents page contains abbreviated/wrapped entries:
    #
    #   11.2 Tools of Recombinant DNA
    #   11.3 Processes of Recombinant
    #
    # The actual headings contain the complete titles:
    #
    #   11.2 TOOLS OF RECOMBINANT DNA TECHNOLOGY
    #   11.3 PROCESSES OF RECOMBINANT DNA TECHNOLOGY
    # ---------------------------------------------------------

    required_titles = {
        "11.1": "PRINCIPLES OF BIOTECHNOLOGY",
        "11.2": "TOOLS OF RECOMBINANT DNA TECHNOLOGY",
        "11.3": "PROCESSES OF RECOMBINANT DNA TECHNOLOGY",
    }

    actual_candidates = []

    for candidate in candidates:
        section_number = candidate["section_number"]
        title = candidate["title"].upper()

        expected_title = required_titles.get(section_number)

        if expected_title is None:
            continue

        if title != expected_title:
            continue

        actual_candidates.append(candidate)

    # Remove duplicate occurrences of the same actual heading.
    unique_candidates = []
    seen = set()

    for candidate in actual_candidates:
        section_number = candidate["section_number"]

        if section_number in seen:
            continue

        seen.add(section_number)
        unique_candidates.append(candidate)

    # Ensure sections are in textbook order.
    unique_candidates.sort(
        key=lambda candidate: candidate["page_number"]
    )

    expected_numbers = ["11.1", "11.2", "11.3"]

    actual_numbers = [
        candidate["section_number"]
        for candidate in unique_candidates
    ]

    if actual_numbers != expected_numbers:
        raise ValueError(
            f"Could not identify the expected sections for "
            f"{class_name} Chapter {chapter_number}. "
            f"Expected {expected_numbers}, "
            f"found {actual_numbers}."
        )

    sections = []

    for index, candidate in enumerate(unique_candidates):
        start_page = candidate["page_number"]

        if index + 1 < len(unique_candidates):
            end_page = (
                unique_candidates[index + 1]["page_number"]
                - 1
            )
        else:
            end_page = pages[-1]["page_number"]

        section_pages = [
            page
            for page in pages
            if start_page <= page["page_number"] <= end_page
        ]

        text_parts = []

        for page in section_pages:
            page_text = page.get("text", "").strip()

            if page_text:
                text_parts.append(page_text)

        sections.append(
            BiologySection(
                section_number=candidate["section_number"],
                title=candidate["title"],
                start_page=start_page,
                end_page=end_page,
                text="\n\n".join(text_parts),
            )
        )

    return sections