import re
from dataclasses import dataclass

import pymupdf

from question_generator.chunker import TextChunk
from question_generator.text_preprocessor import preprocess_text
from question_generator.syllabus_mapper import (
    get_topic_source_chapter,
)
from question_generator.topic_mapper import (
    get_topic_section,
    get_topic_section_end,
)


@dataclass(frozen=True)
class _TextBlock:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str


def _get_page_blocks(
    page: pymupdf.Page,
) -> list[_TextBlock]:
    blocks = page.get_text("blocks")

    text_blocks = [
        _TextBlock(
            x0=block[0],
            y0=block[1],
            x1=block[2],
            y1=block[3],
            text=block[4].strip(),
        )
        for block in blocks
        if block[4].strip()
    ]

    return sorted(
        text_blocks,
        key=lambda block: (
            round(block.y0, 1),
            round(block.x0, 1),
        ),
    )


def _blocks_to_text(
    blocks: list[_TextBlock],
) -> str:
    return "\n".join(
        block.text
        for block in blocks
    )


def _find_section_block(
    blocks: list[_TextBlock],
    section_number: str,
) -> int | None:
    pattern = re.compile(
        rf"^[ \t]*{re.escape(section_number)}[ \t]+"
        r"[A-Z][A-Z0-9 \t\-â€“â€”:,()'&]*[ \t]*$",
        re.MULTILINE,
    )

    for index, block in enumerate(blocks):
        if pattern.search(block.text):
            return index

    return None


def _find_actual_chapter_start(
    pages: list[list[_TextBlock]],
    chapter_name: str,
) -> int:
    chapter_name = chapter_name.upper()

    for page_index, blocks in enumerate(pages):
        page_text = _blocks_to_text(blocks)
        upper_text = page_text.upper()

        if (
            "CHAPTER" in upper_text
            and chapter_name in upper_text
        ):
            return page_index

    raise ValueError(
        f"Could not identify actual chapter start: "
        f"{chapter_name}"
    )


def _find_section_location(
    pages: list[list[_TextBlock]],
    section_number: str,
    start_page: int,
) -> tuple[int, int]:
    for page_index in range(
        start_page,
        len(pages),
    ):
        block_index = _find_section_block(
            pages[page_index],
            section_number,
        )

        if block_index is not None:
            return page_index, block_index

    raise ValueError(
        f"Section not found: {section_number}"
    )


def _find_exercises_start(
    pages: list[list[_TextBlock]],
    start_page: int,
) -> tuple[int, int]:
    pattern = re.compile(
        r"^\s*EXERCISES\s*$",
        re.MULTILINE,
    )

    for page_index in range(
        start_page,
        len(pages),
    ):
        for block_index, block in enumerate(
            pages[page_index]
        ):
            if pattern.search(block.text):
                return page_index, block_index

    raise ValueError(
        "Could not identify exercises boundary."
    )


def extract_topic_text(
    pdf_path: str,
    subject: str,
    chapter: str,
    topic: str,
) -> TextChunk:

    topic_source_chapter = get_topic_source_chapter(
        subject,
        chapter,
        topic,
    )

    start_section = get_topic_section(
        subject,
        chapter,
        topic,
    )

    end_section = get_topic_section_end(
        subject,
        chapter,
        topic,
    )

    with pymupdf.open(pdf_path) as document:
        pages = [
            _get_page_blocks(page)
            for page in document
        ]

    chapter_start = _find_actual_chapter_start(
        pages,
        topic_source_chapter,
    )

    start_page, start_block = _find_section_location(
        pages,
        start_section,
        chapter_start,
    )

    if end_section is not None:
        end_page, end_block = _find_section_location(
            pages,
            end_section,
            start_page,
        )

        if end_page == start_page:
            selected_blocks = pages[start_page][
                start_block:end_block
            ]
        else:
            selected_blocks = []

            selected_blocks.extend(
                pages[start_page][start_block:]
            )

            selected_blocks.extend(
                [
                    block
                    for page_blocks in pages[
                        start_page + 1:end_page
                    ]
                    for block in page_blocks
                ]
            )

            selected_blocks.extend(
                pages[end_page][:end_block]
            )

    else:
        end_page, end_block = _find_exercises_start(
            pages,
            start_page,
        )

        if end_page == start_page:
            selected_blocks = pages[start_page][
                start_block:end_block
            ]
        else:
            selected_blocks = []

            selected_blocks.extend(
                pages[start_page][start_block:]
            )

            selected_blocks.extend(
                [
                    block
                    for page_blocks in pages[
                        start_page + 1:end_page
                    ]
                    for block in page_blocks
                ]
            )

            selected_blocks.extend(
                pages[end_page][:end_block]
            )

    topic_text = _blocks_to_text(
        selected_blocks,
    )

    topic_text = preprocess_text(
        topic_text,
    ).strip()

    if not topic_text:
        raise ValueError(
            f"No text extracted for "
            f"{subject} -> {chapter} -> {topic}"
        )

    return TextChunk(
        subject=subject,
        chapter=chapter,
        topic=topic,
        text=topic_text,
    )