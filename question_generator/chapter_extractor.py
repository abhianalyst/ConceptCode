import re

import pymupdf

from question_generator.chunker import TextChunk
from question_generator.syllabus_mapper import get_source_chapters
from question_generator.text_preprocessor import preprocess_text


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().upper()


def _contains_chapter_heading(
    page_text: str,
    chapter_name: str,
) -> bool:
    page = _normalise(page_text)
    name = _normalise(chapter_name)

    return name in page


def _find_first_occurrence_after(
    pages: list[dict],
    chapter_name: str,
    start_index: int = 0,
) -> int | None:
    for index in range(start_index, len(pages)):
        if _contains_chapter_heading(
            pages[index]["text"],
            chapter_name,
        ):
            return index

    return None


def extract_chapter_text(
    pdf_path: str,
    subject: str,
    syllabus_chapter: str,
) -> TextChunk:

    source_chapters = get_source_chapters(
        subject,
        syllabus_chapter,
    )

    with pymupdf.open(pdf_path) as document:
        pages = [
            {
                "number": index,
                "text": page.get_text("text"),
            }
            for index, page in enumerate(document)
        ]

    # The first occurrence is usually the TOC.
    # Find a later occurrence that has actual chapter content.
    first_source = source_chapters[0]

    candidates = [
        index
        for index, page in enumerate(pages)
        if _contains_chapter_heading(
            page["text"],
            first_source,
        )
    ]

    if len(candidates) < 2:
        raise ValueError(
            f"Could not identify actual chapter start: "
            f"{first_source}"
        )

    start_index = candidates[1]

    # If multiple source chapters are mapped to one syllabus
    # chapter, locate the final mapped chapter after start.
    final_source = source_chapters[-1]

    final_candidates = [
        index
        for index in range(
            start_index,
            len(pages),
        )
        if _contains_chapter_heading(
            pages[index]["text"],
            final_source,
        )
    ]

    if not final_candidates:
        raise ValueError(
            f"Could not identify final source chapter: "
            f"{final_source}"
        )

    final_start_index = final_candidates[0]

    # Find the next chapter after the final mapped chapter.
    end_index = len(pages)

    chapter_pattern = re.compile(
        r"\bCHAPTER\s+(?:ONE|TWO|THREE|FOUR|FIVE|SIX|"
        r"SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|"
        r"FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|"
        r"NINETEEN|TWENTY|\d+)\b",
        re.IGNORECASE,
    )

    for index in range(
        final_start_index + 1,
        len(pages),
    ):
        page_text = pages[index]["text"]

        if chapter_pattern.search(page_text):
            end_index = index
            break

    selected_pages = pages[
        start_index:end_index
    ]

    chapter_text = "\n\n".join(
        page["text"]
        for page in selected_pages
    )

    chapter_text = preprocess_text(
        chapter_text
    )

    if not chapter_text:
        raise ValueError(
            f"No text extracted for "
            f"{subject} -> {syllabus_chapter}"
        )

    return TextChunk(
        subject=subject,
        chapter=syllabus_chapter,
        topic="",
        text=chapter_text,
    )