from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class GenerateBiologyCommandTests(SimpleTestCase):

    @patch(
        "apps.core.management.commands.generate_biology."
        "generate_questions_from_biology_json"
    )
    @patch(
        "apps.core.management.commands.generate_biology."
        "get_gemini_question_provider"
    )
    def test_command_runs_successfully(
        self,
        mock_provider,
        mock_generate,
    ):
        mock_provider.return_value.generate.return_value = []
        mock_generate.return_value = Path("output.json")

        output = StringIO()

        call_command(
            "generate_biology",
            class_name="class_12",
            chapter=11,
            output="output.json",
            stdout=output,
        )

        mock_provider.assert_called_once()
        mock_generate.assert_called_once_with(
            "class_12",
            11,
            Path("output.json"),
            service=mock_generate.call_args.kwargs["service"],
        )

        self.assertIn(
            "Biology question generation completed.",
            output.getvalue(),
        )
        self.assertIn(
            "Output: output.json",
            output.getvalue(),
        )

    def test_class_name_is_required(self):
        with self.assertRaises(CommandError):
            call_command(
                "generate_biology",
                chapter=11,
                output="output.json",
            )

    def test_chapter_is_required(self):
        with self.assertRaises(CommandError):
            call_command(
                "generate_biology",
                class_name="class_12",
                output="output.json",
            )

    def test_output_is_required(self):
        with self.assertRaises(CommandError):
            call_command(
                "generate_biology",
                class_name="class_12",
                chapter=11,
            )

    def test_invalid_class_name_is_rejected(self):
        with self.assertRaises(CommandError):
            call_command(
                "generate_biology",
                class_name="class_10",
                chapter=11,
                output="output.json",
            )
