from django.test import SimpleTestCase

from apps.core.services.biology_sections import (
    BiologySection,
    extract_sections,
)


class BiologySectionTests(SimpleTestCase):

    def test_class_12_chapter_11_has_three_sections(self):
        sections = extract_sections(
            "class_12",
            11,
        )

        self.assertEqual(len(sections), 3)

    def test_section_numbers(self):
        sections = extract_sections(
            "class_12",
            11,
        )

        self.assertEqual(
            [section.section_number for section in sections],
            ["11.1", "11.2", "11.3"],
        )

    def test_section_titles(self):
        sections = extract_sections(
            "class_12",
            11,
        )

        self.assertEqual(
            [section.title for section in sections],
            [
                "PRINCIPLES OF BIOTECHNOLOGY",
                "TOOLS OF RECOMBINANT DNA TECHNOLOGY",
                "PROCESSES OF RECOMBINANT DNA TECHNOLOGY",
            ],
        )

    def test_section_boundaries(self):
        sections = extract_sections(
            "class_12",
            11,
        )

        self.assertEqual(
            [
                (
                    section.start_page,
                    section.end_page,
                )
                for section in sections
            ],
            [
                (203, 204),
                (205, 210),
                (211, 214),
            ],
        )

    def test_sections_have_text(self):
        sections = extract_sections(
            "class_12",
            11,
        )

        self.assertTrue(
            all(section.text.strip() for section in sections)
        )

    def test_section_is_biology_section(self):
        sections = extract_sections(
            "class_12",
            11,
        )

        self.assertTrue(
            all(
                isinstance(section, BiologySection)
                for section in sections
            )
        )

    def test_topic_matches_title(self):
        sections = extract_sections(
            "class_12",
            11,
        )

        self.assertEqual(
            sections[0].topic,
            "PRINCIPLES OF BIOTECHNOLOGY",
        )