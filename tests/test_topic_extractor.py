from django.test import SimpleTestCase

from question_generator.schemas import Section
from question_generator.sections import extract_sections


class SectionExtractorIntegrationTests(SimpleTestCase):

    def test_extracts_class_12_chapter_11_sections(self):
        pages = []

        from apps.core.services.biology_source import get_chapter_pages

        pages = get_chapter_pages("class_12", 11)

        sections = extract_sections(
            pages,
            source="class_12_biology.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

        self.assertEqual(len(sections), 3)

        self.assertEqual(
            [section.number for section in sections],
            ["11.1", "11.2", "11.3"],
        )

    def test_section_titles_are_extracted(self):
        from apps.core.services.biology_source import get_chapter_pages

        sections = extract_sections(
            get_chapter_pages("class_12", 11),
            source="class_12_biology.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

        self.assertEqual(
            sections[0].title,
            "PRINCIPLES OF BIOTECHNOLOGY",
        )

    def test_sections_have_valid_page_ranges(self):
        from apps.core.services.biology_source import get_chapter_pages

        sections = extract_sections(
            get_chapter_pages("class_12", 11),
            source="class_12_biology.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

        for section in sections:
            self.assertGreaterEqual(section.page_start, 201)
            self.assertLessEqual(section.page_end, 214)
            self.assertLessEqual(
                section.page_start,
                section.page_end,
            )

    def test_sections_contain_text(self):
        from apps.core.services.biology_source import get_chapter_pages

        sections = extract_sections(
            get_chapter_pages("class_12", 11),
            source="class_12_biology.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

        self.assertTrue(
            all(section.text.strip() for section in sections)
        )

    def test_section_text_does_not_include_next_heading(self):
        from apps.core.services.biology_source import get_chapter_pages

        sections = extract_sections(
            get_chapter_pages("class_12", 11),
            source="class_12_biology.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

        for current, following in zip(
            sections,
            sections[1:],
        ):
            next_heading = (
                f"{following.number} "
                f"{following.title}"
            )

            self.assertNotIn(
                next_heading,
                current.text,
            )

    def test_section_is_immutable(self):
        section = Section(
            section_id="biology_12.pdf-11.1",
            number="11.1",
            title="PRINCIPLES OF BIOTECHNOLOGY",
            text="Example text.",
            source="biology_12.pdf",
            page_start=203,
            page_end=204,
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
        )

        with self.assertRaises(AttributeError):
            section.title = "Changed"
