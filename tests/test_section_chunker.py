from django.test import SimpleTestCase

from question_generator.chunking import chunk_section
from question_generator.schemas import Section


class SectionChunkerTests(SimpleTestCase):

    def setUp(self):
        self.section = Section(
            section_id="biology_12.pdf-11.1",
            number="11.1",
            title="PRINCIPLES OF BIOTECHNOLOGY",
            text=(
                "Biotechnology deals with techniques.\n\n"
                "Genetic engineering alters genetic material.\n\n"
                "Bioprocess engineering maintains sterile conditions."
            ),
            source="biology_12.pdf",
            page_start=203,
            page_end=205,
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
        )

    def test_chunks_section(self):
        chunks = chunk_section(
            self.section,
            chunk_size=80,
            overlap=10,
        )

        self.assertTrue(chunks)

    def test_preserves_section_metadata(self):
        chunks = chunk_section(
            self.section,
            chunk_size=80,
            overlap=10,
        )

        for chunk in chunks:
            self.assertEqual(
                chunk.source,
                "biology_12.pdf",
            )
            self.assertEqual(
                chunk.subject,
                "Biology",
            )
            self.assertEqual(
                chunk.chapter,
                "Biotechnology: Principles and Processes",
            )
            self.assertEqual(
                chunk.topic,
                "PRINCIPLES OF BIOTECHNOLOGY",
            )
            self.assertEqual(
                chunk.page_start,
                203,
            )
            self.assertEqual(
                chunk.page_end,
                205,
            )

    def test_empty_section_returns_no_chunks(self):
        empty = Section(
            section_id="empty",
            number="11.1",
            title="PRINCIPLES OF BIOTECHNOLOGY",
            text="",
            source="biology_12.pdf",
            page_start=203,
            page_end=205,
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
        )

        self.assertEqual(
            chunk_section(empty),
            [],
        )