from django.test import SimpleTestCase

from question_generator.chunking import Chunk, chunk_text


class ChunkerTests(SimpleTestCase):

    def test_empty_text_returns_no_chunks(self):
        self.assertEqual(
            chunk_text(""),
            [],
        )

    def test_whitespace_only_returns_no_chunks(self):
        self.assertEqual(
            chunk_text("   \n\n   "),
            [],
        )

    def test_returns_chunk_objects(self):
        chunks = chunk_text(
            "Paragraph one.\n\nParagraph two.",
            chunk_size=100,
            overlap=20,
        )

        self.assertTrue(chunks)
        self.assertIsInstance(chunks[0], Chunk)

    def test_paragraphs_are_preserved(self):
        text = (
            "Paragraph one.\n\n"
            "Paragraph two."
        )

        chunks = chunk_text(
            text,
            chunk_size=100,
            overlap=20,
        )

        self.assertEqual(
            chunks[0].text,
            text,
        )

    def test_metadata_is_preserved(self):
        chunks = chunk_text(
            "Biology content.",
            source="biology_12.pdf",
            page_start=201,
            page_end=214,
            subject="Biology",
            chapter="Biotechnology",
            topic="Bioreactors",
        )

        chunk = chunks[0]

        self.assertEqual(
            chunk.source,
            "biology_12.pdf",
        )
        self.assertEqual(chunk.page_start, 201)
        self.assertEqual(chunk.page_end, 214)
        self.assertEqual(chunk.subject, "Biology")
        self.assertEqual(chunk.chapter, "Biotechnology")
        self.assertEqual(chunk.topic, "Bioreactors")

    def test_chunk_ids_are_unique(self):
        text = (
            "A" * 80
            + "\n\n"
            + "B" * 80
            + "\n\n"
            + "C" * 80
        )

        chunks = chunk_text(
            text,
            chunk_size=100,
            overlap=20,
        )

        ids = [chunk.chunk_id for chunk in chunks]

        self.assertEqual(
            len(ids),
            len(set(ids)),
        )

    def test_invalid_chunk_size_raises_error(self):
        with self.assertRaises(ValueError):
            chunk_text(
                "Some text.",
                chunk_size=0,
            )

    def test_negative_overlap_raises_error(self):
        with self.assertRaises(ValueError):
            chunk_text(
                "Some text.",
                overlap=-1,
            )

    def test_overlap_must_be_smaller_than_chunk_size(self):
        with self.assertRaises(ValueError):
            chunk_text(
                "Some text.",
                chunk_size=100,
                overlap=100,
            )

    def test_non_string_text_raises_type_error(self):
        with self.assertRaises(TypeError):
            chunk_text(None)
