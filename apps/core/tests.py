from django.test import TestCase

from apps.core.services.biology_source import (
    get_chapter_pages,
)


class BiologySourceTests(TestCase):

    def test_class_11_chapter_1_pages(self):
        pages = get_chapter_pages("class_11", 1)

        self.assertTrue(pages)
        self.assertEqual(pages[0]["page_number"], 11)
        self.assertEqual(pages[-1]["page_number"], 23)

    def test_class_12_chapter_1_pages(self):
        pages = get_chapter_pages("class_12", 1)

        self.assertTrue(pages)
        self.assertEqual(pages[0]["page_number"], 11)
        self.assertEqual(pages[-1]["page_number"], 26)

    def test_class_12_chapter_11_pages(self):
        pages = get_chapter_pages("class_12", 11)

        self.assertTrue(pages)
        self.assertEqual(pages[0]["page_number"], 201)
        self.assertEqual(pages[-1]["page_number"], 214)

    def test_pages_are_contiguous(self):
        pages = get_chapter_pages("class_12", 11)

        page_numbers = [
            page["page_number"]
            for page in pages
        ]

        expected = list(range(201, 215))

        self.assertEqual(page_numbers, expected)

    def test_invalid_chapter_raises_error(self):
        with self.assertRaises(ValueError):
            get_chapter_pages("class_12", 17)

    def test_invalid_class_raises_error(self):
        with self.assertRaises(ValueError):
            get_chapter_pages("class_13", 1)

    def test_chapter_number_must_be_integer(self):
        with self.assertRaises(ValueError):
            get_chapter_pages("class_12", "11")