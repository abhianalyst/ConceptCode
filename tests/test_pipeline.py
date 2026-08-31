from django.core.serializers import python

python
import json
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from question_generator.pipeline import pdf_to_json
from question_generator.schemas import Document, Page


class PipelineTests(SimpleTestCase):

    def test_pdf_to_json_creates_structured_json(self):
        document = Document(
            filename="tmp_pipeline.pdf",
            title="Test PDF",
            page_count=1,
            pages=[
                Page(
                    page_number=1,
                    text="Hello from PDF.",
                    blocks=[],
                )
            ],
        )

        output_path = Path("tests/tmp_pipeline_output.json")

        try:
            with patch(
                "question_generator.pipeline.extract_pdf",
                return_value=document,
            ):
                result = pdf_to_json(
                    "tests/tmp_pipeline.pdf",
                    output_path,
                )

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())

            data = json.loads(
                output_path.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                data["document"]["filename"],
                "tmp_pipeline.pdf",
            )

            self.assertEqual(
                data["document"]["title"],
                "Test PDF",
            )

            self.assertEqual(
                data["document"]["page_count"],
                1,
            )

            self.assertEqual(
                data["pages"][0]["page_number"],
                1,
            )

            self.assertEqual(
                data["pages"][0]["text"],
                "Hello from PDF.",
            )

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_pdf_to_json_creates_parent_directory(self):
        document = Document(
            filename="tmp_pipeline.pdf",
            title="Test PDF",
            page_count=1,
            pages=[],
        )

        output_path = Path(
            "tests/tmp_pipeline_output/nested/result.json"
        )

        try:
            with patch(
                "question_generator.pipeline.extract_pdf",
                return_value=document,
            ):
                result = pdf_to_json(
                    "tests/tmp_pipeline.pdf",
                    output_path,
                )

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())

        finally:
            if output_path.exists():
                output_path.unlink()

            parent = output_path.parent

            while parent != Path("tests") and parent.exists():
                try:
                    parent.rmdir()
                except OSError:
                    break

                parent = parent.parent
