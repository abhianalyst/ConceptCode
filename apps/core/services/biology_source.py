import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]

BIOLOGY_DATA_DIR = BASE_DIR / "data" / "books" / "biology"


BOOKS = {
    "class_11": BIOLOGY_DATA_DIR / "biology_11.json",
    "class_12": BIOLOGY_DATA_DIR / "biology_12.json",
}


EXPECTED_CHAPTERS = {
    "class_11": 22,
    "class_12": 16,
}


CHAPTER_START_PATTERN = re.compile(
    r"^\s*CHAPTER\s+(\d+)\s*$",
    re.IGNORECASE,
)


def load_book(class_name):
    """
    Load a Biology JSON book.

    Supported:
        class_11
        class_12
    """

    if class_name not in BOOKS:
        raise ValueError(
            f"Unknown Biology book: {class_name}"
        )

    path = BOOKS[class_name]

    if not path.exists():
        raise FileNotFoundError(
            f"Biology source file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_pages(class_name):
    """
    Return pages from a Biology JSON book.
    """

    data = load_book(class_name)

    pages = data.get("pages")

    if not isinstance(pages, list):
        raise ValueError(
            f"Invalid JSON structure in {class_name}: "
            "'pages' must be a list."
        )

    return pages


def detect_chapter_starts(class_name):
    """
    Find exact CHAPTER N headings in the extracted JSON.

    This returns raw candidates. It does not yet decide which
    candidates represent the actual chapter boundaries.
    """

    pages = get_pages(class_name)

    expected_chapters = EXPECTED_CHAPTERS[class_name]

    chapter_starts = []

    for page in pages:
        page_number = page.get("page_number")
        text = page.get("text", "")

        for line in text.splitlines():
            line = line.strip()

            match = CHAPTER_START_PATTERN.match(line)

            if not match:
                continue

            chapter_number = int(match.group(1))

            if 1 <= chapter_number <= expected_chapters:
                chapter_starts.append(
                    {
                        "chapter_number": chapter_number,
                        "page_number": page_number,
                    }
                )

    return chapter_starts


def extract_chapter_boundaries(class_name):
    """
    Extract chapter boundaries from the NCERT CONTENTS section.

    CONTENTS contains the authoritative printed textbook page
    numbers. The JSON page numbers include front-matter pages,
    so a page offset is calculated and applied.
    """

    pages = get_pages(class_name)
    expected_chapters = EXPECTED_CHAPTERS[class_name]

    # ---------------------------------------------------------
    # 1. Locate CONTENTS pages
    # ---------------------------------------------------------

    contents_page_indexes = [
        index
        for index, page in enumerate(pages)
        if "CONTENTS" in page.get("text", "").upper()
    ]

    if not contents_page_indexes:
        raise ValueError(
            f"Could not locate CONTENTS section for {class_name}."
        )

    contents_start_index = contents_page_indexes[0]

    contents_pages = []

    found_chapters = set()

    for index in range(contents_start_index, len(pages)):
        page = pages[index]
        contents_pages.append(page)

        chapter_numbers = re.findall(
            r"\bChapter\s+(\d+)\b",
            page.get("text", ""),
            re.IGNORECASE,
        )

        for number in chapter_numbers:
            number = int(number)

            if 1 <= number <= expected_chapters:
                found_chapters.add(number)

        if len(found_chapters) == expected_chapters:
            break

    # ---------------------------------------------------------
    # 2. Extract chapter numbers and printed page numbers
    # ---------------------------------------------------------

    chapter_entries = []

    chapter_line_pattern = re.compile(
        r"Chapter\s+(\d+)\s*:?",
        re.IGNORECASE,
    )

    for page in contents_pages:
        lines = page.get("text", "").splitlines()

        for index, line in enumerate(lines):
            match = chapter_line_pattern.search(line)

            if not match:
                continue

            chapter_number = int(match.group(1))

            if not (
                1 <= chapter_number <= expected_chapters
            ):
                continue

            printed_page = None

            # Search forward until the next standalone page number.
            # This handles wrapped chapter titles such as:
            #
            # Chapter 9
            # : Strategies for Enhancement in
            # 165
            # Food Production
            #
            # and normal entries such as:
            #
            # Chapter 11
            # : Biotechnology : Principles and Processes
            # 193

            for next_line in lines[index + 1:]:
                next_line = next_line.strip()

                if next_line.isdigit():
                    printed_page = int(next_line)
                    break

                # Stop if another chapter starts before
                # finding a page number.
                if chapter_line_pattern.search(next_line):
                    break

            if printed_page is None:
                continue

            chapter_entries.append(
                {
                    "chapter_number": chapter_number,
                    "printed_page": printed_page,
                }
            )

    # ---------------------------------------------------------
    # 3. Remove duplicates
    # ---------------------------------------------------------

    unique_entries = []
    seen = set()

    for entry in chapter_entries:
        number = entry["chapter_number"]

        if number in seen:
            continue

        seen.add(number)
        unique_entries.append(entry)

    # ---------------------------------------------------------
    # 4. Validate chapter sequence
    # ---------------------------------------------------------

    expected_numbers = list(
        range(1, expected_chapters + 1)
    )

    actual_numbers = [
        entry["chapter_number"]
        for entry in unique_entries
    ]

    if actual_numbers != expected_numbers:
        raise ValueError(
            f"Invalid chapter sequence for {class_name}. "
            f"Expected {expected_numbers}, "
            f"found {actual_numbers}. "
            f"Entries: {unique_entries}"
        )

    # ---------------------------------------------------------
    # 5. Find actual Chapter 1 page
    # ---------------------------------------------------------

    chapter_1_title_patterns = {
        "class_11": "THE LIVING WORLD",
        "class_12": "REPRODUCTION IN ORGANISMS",
    }

    title = chapter_1_title_patterns[class_name]

    actual_chapter_1_page = None

    for page in pages:
        text = page.get("text", "").upper()

        if "CONTENTS" in text:
            continue

        if (
            title in text
            and "CHAPTER 1" in text
        ):
            actual_chapter_1_page = page["page_number"]
            break

    if actual_chapter_1_page is None:
        raise ValueError(
            f"Could not locate actual Chapter 1 "
            f"for {class_name}."
        )

    # ---------------------------------------------------------
    # 6. Calculate PDF page offset
    # ---------------------------------------------------------

    printed_chapter_1_page = unique_entries[0][
        "printed_page"
    ]

    page_offset = (
        actual_chapter_1_page
        - printed_chapter_1_page
    )

    # ---------------------------------------------------------
    # 7. Convert printed pages to JSON pages
    # ---------------------------------------------------------

    starts = []

    for entry in unique_entries:
        starts.append(
            {
                "chapter_number": entry["chapter_number"],
                "start_page": (
                    entry["printed_page"]
                    + page_offset
                ),
            }
        )

    # ---------------------------------------------------------
    # 8. Calculate boundaries
    # ---------------------------------------------------------

    last_page_number = pages[-1]["page_number"]

    boundaries = []

    for index, item in enumerate(starts):

        start_page = item["start_page"]

        if index + 1 < len(starts):
            end_page = (
                starts[index + 1]["start_page"]
                - 1
            )
        else:
            end_page = last_page_number

        boundaries.append(
            {
                "chapter_number": item["chapter_number"],
                "start_page": start_page,
                "end_page": end_page,
            }
        )

    return boundaries

def get_chapter_pages(class_name, chapter_number):
    """
    Return the JSON pages belonging to a specific Biology chapter.
    """

    if not isinstance(chapter_number, int):
        raise ValueError(
            "chapter_number must be an integer."
        )

    boundaries = extract_chapter_boundaries(class_name)

    chapter = next(
        (
            item
            for item in boundaries
            if item["chapter_number"] == chapter_number
        ),
        None,
    )

    if chapter is None:
        raise ValueError(
            f"Chapter {chapter_number} does not exist "
            f"in {class_name}."
        )

    pages = get_pages(class_name)

    start_page = chapter["start_page"]
    end_page = chapter["end_page"]

    return [
        page
        for page in pages
        if start_page <= page["page_number"] <= end_page
    ]