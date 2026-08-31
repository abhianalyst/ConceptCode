from django.test import SimpleTestCase

from question_generator.sections import extract_sections


class SectionExtractorTests(SimpleTestCase):

    def test_extracts_numbered_sections(self):
        pages = [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "text": (
                            "11.1 PRINCIPLES OF BIOTECHNOLOGY\n"
                            "Biotechnology deals with techniques."
                        )
                    }
                ],
            },
            {
                "page_number": 2,
                "blocks": [
                    {
                        "text": (
                            "More information about biotechnology."
                        )
                    }
                ],
            },
            {
                "page_number": 3,
                "blocks": [
                    {
                        "text": (
                            "11.2 TOOLS OF RECOMBINANT DNA TECHNOLOGY\n"
                            "Several tools are used."
                        )
                    }
                ],
            },
        ]

        sections = extract_sections(
            pages,
            source="biology_12.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

        self.assertEqual(len(sections), 2)

        self.assertEqual(
            sections[0].number,
            "11.1",
        )

        self.assertEqual(
            sections[0].title,
            "PRINCIPLES OF BIOTECHNOLOGY",
        )

        self.assertIn(
            "Biotechnology deals with techniques.",
            sections[0].text,
        )

        self.assertIn(
            "More information about biotechnology.",
            sections[0].text,
        )

        self.assertEqual(
            sections[0].page_start,
            1,
        )

        self.assertEqual(
            sections[0].page_end,
            2,
        )

        self.assertEqual(
            sections[1].number,
            "11.2",
        )

    def test_ignores_title_case_toc_entries(self):
        pages = [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "text": (
                            "11.1 Principles of Biotechnology\n"
                            "11.2 Tools of Recombinant DNA"
                        )
                    }
                ],
            },
            {
                "page_number": 2,
                "blocks": [
                    {
                        "text": (
                            "11.1 PRINCIPLES OF BIOTECHNOLOGY\n"
                            "Biotechnology content."
                        )
                    }
                ],
            },
            {
                "page_number": 3,
                "blocks": [
                    {
                        "text": (
                            "11.2 TOOLS OF RECOMBINANT DNA TECHNOLOGY\n"
                            "Recombinant DNA content."
                        )
                    }
                ],
            },
        ]

        sections = extract_sections(
            pages,
            source="biology_12.pdf",
            chapter="Biotechnology: Principles and Processes",
            subject="Biology",
        )

        self.assertEqual(len(sections), 2)

        self.assertEqual(sections[0].number, "11.1")
        self.assertEqual(
            sections[0].title,
            "PRINCIPLES OF BIOTECHNOLOGY",
        )

        self.assertEqual(sections[0].page_start, 2)
        self.assertEqual(sections[0].page_end, 2)

        self.assertEqual(sections[1].number, "11.2")
        self.assertEqual(
            sections[1].title,
            "TOOLS OF RECOMBINANT DNA TECHNOLOGY",
        )    