from pathlib import Path
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from question_generator.cli import (
    build_parser,
    generate_questions_from_pdf,
)


class QuestionGeneratorCLITests(SimpleTestCase):

    def test_parser_requires_input(self):
        parser = build_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_parser_accepts_generation_arguments(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "--input",
                "biology.pdf",
                "--output",
                "questions.json",
                "--subject",
                "Biology",
                "--chapter",
                "Biotechnology",
            ]
        )

        self.assertEqual(
            args.input,
            "biology.pdf",
        )

        self.assertEqual(
            args.output,
            "questions.json",
        )

        self.assertEqual(
            args.subject,
            "Biology",
        )

        self.assertEqual(
            args.chapter,
            "Biotechnology",
        )

    @patch(
        "question_generator.cli.export_questions_json"
    )
    @patch(
        "apps.core.services.question_generation."
        "get_question_generation_service"
    )
    @patch(
        "question_generator.cli.generate_questions_from_sections"
    )
    @patch(
        "question_generator.cli.extract_sections"
    )
    @patch(
        "question_generator.cli.extract_pdf"
    )
    def test_generation_pipeline(
        self,
        mock_extract_pdf,
        mock_extract_sections,
        mock_generate,
        mock_get_service,
        mock_export,
    ):
        document = Mock()

        document.filename = "biology.pdf"
        document.page_count = 1

        page = Mock()

        page.to_dict.return_value = {
            "page_number": 1,
            "text": "Biology content",
            "blocks": [],
        }

        document.pages = [page]

        mock_extract_pdf.return_value = document

        section = Mock()

        mock_extract_sections.return_value = [
            section,
        ]

        service = Mock()

        mock_get_service.return_value = service

        questions = [
            Mock(),
        ]

        mock_generate.return_value = questions

        output = Path("questions.json")

        mock_export.return_value = output

        result = generate_questions_from_pdf(
            "biology.pdf",
            output,
            subject="Biology",
            chapter="Biotechnology",
        )

        self.assertEqual(
            result,
            output,
        )

        mock_extract_pdf.assert_called_once_with(
            Path("biology.pdf"),
        )

        mock_extract_sections.assert_called_once_with(
            [
                {
                    "page_number": 1,
                    "text": "Biology content",
                    "blocks": [],
                }
            ],
            source="biology.pdf",
            chapter="Biotechnology",
            subject="Biology",
        )

        mock_get_service.assert_called_once()

        mock_generate.assert_called_once_with(
            [section],
            subject="Biology",
            source="biology.pdf",
            service=service,
        )

        mock_export.assert_called_once_with(
            questions,
            output,
            source_file="biology.pdf",
        )

    def test_rejects_empty_subject(self):
        with self.assertRaises(ValueError):
            generate_questions_from_pdf(
                "biology.pdf",
                "questions.json",
                subject="",
                chapter="Biotechnology",
            )

    def test_rejects_empty_chapter(self):
        with self.assertRaises(ValueError):
            generate_questions_from_pdf(
                "biology.pdf",
                "questions.json",
                subject="Biology",
                chapter="",
            )