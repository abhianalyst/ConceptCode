
from pathlib import Path
from unittest.mock import mock_open, patch

from django.test import SimpleTestCase

from apps.core.services.biology_source import (
    BOOKS,
    EXPECTED_CHAPTERS,
    detect_chapter_starts,
    extract_chapter_boundaries,
    get_chapter_pages,
    get_pages,
    load_book,
)


class BiologySourceTests(SimpleTestCase):

    def test_books_contains_supported_classes(self):
        self.assertIn("class_11", BOOKS)
        self.assertIn("class_12", BOOKS)

    def test_expected_chapter_counts(self):
        self.assertEqual(
            EXPECTED_CHAPTERS["class_11"],
            22,
        )

        self.assertEqual(
            EXPECTED_CHAPTERS["class_12"],
            16,
        )

    def test_load_book_rejects_unknown_class(self):
        with self.assertRaises(ValueError):
            load_book("class_10")

    def test_load_book_raises_when_file_missing(self):
        with patch(
            "apps.core.services.biology_source.BOOKS",
            {
                "class_11": Path(
                    "definitely_missing_book.json"
                ),
            },
        ):
            with self.assertRaises(FileNotFoundError):
                load_book("class_11")

    def test_load_book_reads_json(self):
        fake_json = (
            '{"pages": [{"page_number": 1}]}'
        )

        fake_path = Path("fake-book.json")

        with patch(
            "apps.core.services.biology_source.BOOKS",
            {
                "class_11": fake_path,
            },
        ), patch.object(
            Path,
            "exists",
            return_value=True,
        ), patch.object(
            Path,
            "open",
            mock_open(read_data=fake_json),
        ):
            data = load_book("class_11")

        self.assertEqual(
            data,
            {
                "pages": [
                    {
                        "page_number": 1,
                    }
                ]
            },
        )

    def test_get_pages_returns_page_list(self):
        fake_pages = [
            {
                "page_number": 1,
            },
            {
                "page_number": 2,
            },
        ]

        with patch(
            "apps.core.services.biology_source.load_book",
            return_value={
                "pages": fake_pages,
            },
        ):
            pages = get_pages("class_11")

        self.assertEqual(
            pages,
            fake_pages,
        )

    def test_get_pages_rejects_invalid_structure(self):
        with patch(
            "apps.core.services.biology_source.load_book",
            return_value={
                "pages": {},
            },
        ):
            with self.assertRaises(ValueError):
                get_pages("class_11")

    def test_detect_chapter_starts_finds_valid_chapters(self):
        pages = [
            {
                "page_number": 1,
                "text": (
                    "CHAPTER 1\n"
                    "The Living World"
                ),
            },
            {
                "page_number": 10,
                "text": (
                    "CHAPTER 2\n"
                    "Biological Classification"
                ),
            },
        ]

        with patch(
            "apps.core.services.biology_source.get_pages",
            return_value=pages,
        ):
            with patch(
                "apps.core.services.biology_source.EXPECTED_CHAPTERS",
                {
                    "class_11": 22,
                },
            ):
                starts = detect_chapter_starts(
                    "class_11"
                )

        self.assertEqual(
            starts,
            [
                {
                    "chapter_number": 1,
                    "page_number": 1,
                },
                {
                    "chapter_number": 2,
                    "page_number": 10,
                },
            ],
        )

    def test_detect_chapter_starts_ignores_invalid_chapter_numbers(
        self,
    ):
        pages = [
            {
                "page_number": 1,
                "text": "CHAPTER 0",
            },
            {
                "page_number": 2,
                "text": "CHAPTER 1",
            },
            {
                "page_number": 3,
                "text": "CHAPTER 23",
            },
        ]

        with patch(
            "apps.core.services.biology_source.get_pages",
            return_value=pages,
        ):
            starts = detect_chapter_starts(
                "class_11"
            )

        self.assertEqual(
            starts,
            [
                {
                    "chapter_number": 1,
                    "page_number": 2,
                },
            ],
        )

    def test_detect_chapter_starts_ignores_non_matching_lines(
        self,
    ):
        pages = [
            {
                "page_number": 1,
                "text": (
                    "CONTENTS\n"
                    "Chapter ONE\n"
                    "CHAPTER ONE\n"
                    "CHAPTER 1 EXTRA\n"
                    "Chapter 2 : Biology\n"
                    "Ordinary textbook text\n"
                    "1.1 INTRODUCTION"
                ),
            }
        ]

        with patch(
            "apps.core.services.biology_source.get_pages",
            return_value=pages,
        ):
            starts = detect_chapter_starts(
                "class_11"
            )

        self.assertEqual(
            starts,
            [],
        )

    def test_extract_chapter_boundaries_class_12(self):
        boundaries = extract_chapter_boundaries(
            "class_12"
        )

        self.assertEqual(
            len(boundaries),
            16,
        )

        self.assertEqual(
            boundaries[0]["chapter_number"],
            1,
        )

        self.assertEqual(
            boundaries[-1]["chapter_number"],
            16,
        )

        for index, boundary in enumerate(
            boundaries
        ):
            self.assertLessEqual(
                boundary["start_page"],
                boundary["end_page"],
            )

            if index > 0:
                self.assertEqual(
                    boundary["start_page"],
                    boundaries[index - 1]["end_page"] + 1,
                )

    def test_extract_chapter_boundaries_class_11(self):
        boundaries = extract_chapter_boundaries(
            "class_11"
        )

        self.assertEqual(
            len(boundaries),
            22,
        )

        self.assertEqual(
            boundaries[0]["chapter_number"],
            1,
        )

        self.assertEqual(
            boundaries[-1]["chapter_number"],
            22,
        )

    def test_get_chapter_pages_returns_only_requested_chapter(
        self,
    ):
        pages = [
            {
                "page_number": 10,
                "text": "chapter 1",
            },
            {
                "page_number": 11,
                "text": "chapter 1 continued",
            },
            {
                "page_number": 12,
                "text": "chapter 2",
            },
        ]

        fake_boundaries = [
            {
                "chapter_number": 1,
                "start_page": 10,
                "end_page": 11,
            },
            {
                "chapter_number": 2,
                "start_page": 12,
                "end_page": 20,
            },
        ]

        with patch(
            "apps.core.services.biology_source.extract_chapter_boundaries",
            return_value=fake_boundaries,
        ), patch(
            "apps.core.services.biology_source.get_pages",
            return_value=pages,
        ):
            result = get_chapter_pages(
                "class_11",
                1,
            )

        self.assertEqual(
            result,
            [
                {
                    "page_number": 10,
                    "text": "chapter 1",
                },
                {
                    "page_number": 11,
                    "text": "chapter 1 continued",
                },
            ],
        )

    def test_get_chapter_pages_rejects_non_integer(self):
        with self.assertRaises(ValueError):
            get_chapter_pages(
                "class_11",
                "1",
            )

    def test_get_chapter_pages_rejects_unknown_chapter(self):
        fake_boundaries = [
            {
                "chapter_number": 1,
                "start_page": 10,
                "end_page": 20,
            }
        ]

        with patch(
            "apps.core.services.biology_source.extract_chapter_boundaries",
            return_value=fake_boundaries,
        ):
            with self.assertRaises(ValueError):
                get_chapter_pages(
                    "class_11",
                    2,
                )