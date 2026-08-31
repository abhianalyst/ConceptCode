from django.test import TestCase

from apps.core.services.biology_source import (
    BOOKS,
    EXPECTED_CHAPTERS,
    detect_chapter_starts,
    extract_chapter_boundaries,
    get_pages,
    load_book,
)


class BiologySourceTests(TestCase):

    def test_books_exist(self):
        for class_name, path in BOOKS.items():
            self.assertTrue(
                path.exists(),
                f"Missing Biology source: {path}",
            )

    def test_expected_chapter_counts(self):
        self.assertEqual(
            EXPECTED_CHAPTERS["class_11"],
            22,
        )
        self.assertEqual(
            EXPECTED_CHAPTERS["class_12"],
            16,
        )

    def test_load_books(self):
        class_11 = load_book("class_11")
        class_12 = load_book("class_12")

        self.assertIsInstance(class_11, dict)
        self.assertIsInstance(class_12, dict)

    def test_get_pages_returns_lists(self):
        self.assertIsInstance(
            get_pages("class_11"),
            list,
        )
        self.assertIsInstance(
            get_pages("class_12"),
            list,
        )

    def test_detect_chapter_starts_returns_candidates(self):
        class_11 = detect_chapter_starts("class_11")
        class_12 = detect_chapter_starts("class_12")

        self.assertTrue(class_11)
        self.assertTrue(class_12)

    def test_class_11_boundaries(self):
        chapters = extract_chapter_boundaries("class_11")

        self.assertEqual(len(chapters), 22)

        self.assertEqual(
            [chapter["chapter_number"] for chapter in chapters],
            list(range(1, 23)),
        )

        for chapter in chapters:
            self.assertLessEqual(
                chapter["start_page"],
                chapter["end_page"],
            )

    def test_class_12_boundaries(self):
        chapters = extract_chapter_boundaries("class_12")

        self.assertEqual(len(chapters), 16)

        self.assertEqual(
            [chapter["chapter_number"] for chapter in chapters],
            list(range(1, 17)),
        )

        for chapter in chapters:
            self.assertLessEqual(
                chapter["start_page"],
                chapter["end_page"],
            )

    def test_class_12_includes_chapters_11_to_16(self):
        chapters = extract_chapter_boundaries("class_12")

        chapter_numbers = [
            chapter["chapter_number"]
            for chapter in chapters
        ]

        self.assertIn(11, chapter_numbers)
        self.assertIn(12, chapter_numbers)
        self.assertIn(13, chapter_numbers)
        self.assertIn(14, chapter_numbers)
        self.assertIn(15, chapter_numbers)
        self.assertIn(16, chapter_numbers)

    def test_unknown_book_raises_value_error(self):
        with self.assertRaises(ValueError):
            load_book("class_13")