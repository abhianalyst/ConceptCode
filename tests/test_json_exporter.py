import json
from pathlib import Path

from django.test import SimpleTestCase

from question_generator.output import (
    GENERATOR_VERSION,
    export_questions_json,
    questions_to_dict,
)
from question_generator.schemas import Question


class JSONExporterTests(SimpleTestCase):

    def make_question(self):
        return Question(
            question="What carries genetic information?",
            options=[
                "DNA",
                "RNA",
                "Protein",
                "Lipid",
            ],
            correct_answer="DNA",
            explanation="DNA carries genetic information.",
            difficulty="Easy",
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
        )

    def test_questions_to_dict_contains_metadata(self):
        data = questions_to_dict(
            [self.make_question()],
            source_file="biology_12.pdf",
        )

        self.assertIn(
            "generated_at",
            data["metadata"],
        )

        self.assertEqual(
            data["metadata"]["source_file"],
            "biology_12.pdf",
        )

        self.assertEqual(
            data["metadata"]["generator_version"],
            GENERATOR_VERSION,
        )

        self.assertIn(
            "generated_at",
            data["metadata"],
        )

    def test_questions_to_dict_contains_questions(self):
        data = questions_to_dict(
            [self.make_question()],
            source_file="biology_12.pdf",
        )

        self.assertEqual(
            len(data["questions"]),
            1,
        )

        self.assertEqual(
            data["questions"][0]["question"],
            "What carries genetic information?",
        )

    def test_questions_to_dict_preserves_question_structure(self):
        data = questions_to_dict(
            [self.make_question()],
            source_file="biology_12.pdf",
        )

        question = data["questions"][0]

        self.assertEqual(
            len(question["options"]),
            4,
        )

        self.assertEqual(
            question["correct_answer"],
            "DNA",
        )

        self.assertEqual(
            question["difficulty"],
            "Easy",
        )

        self.assertEqual(
            question["subject"],
            "Biology",
        )

    def test_export_questions_json_creates_file(self):
        output = Path(
            "tests/tmp_export_questions.json"
        )

        try:
            result = export_questions_json(
                [self.make_question()],
                output,
                source_file="biology_12.pdf",
            )

            self.assertEqual(
                result,
                output,
            )

            self.assertTrue(
                output.exists(),
            )

        finally:
            if output.exists():
                output.unlink()

    def test_exported_json_is_valid(self):
        output = Path(
            "tests/tmp_export_questions.json"
        )

        try:
            export_questions_json(
                [self.make_question()],
                output,
                source_file="biology_12.pdf",
            )

            with output.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            self.assertIn(
                "metadata",
                data,
            )

            self.assertIn(
                "questions",
                data,
            )

            self.assertEqual(
                len(data["questions"]),
                1,
            )

        finally:
            if output.exists():
                output.unlink()

    def test_rejects_non_list(self):
        with self.assertRaises(TypeError):
            questions_to_dict(
                "invalid",
                source_file="biology_12.pdf",
            )

    def test_rejects_invalid_question_objects(self):
        with self.assertRaises(TypeError):
            questions_to_dict(
                ["invalid"],
                source_file="biology_12.pdf",
            )

    def test_rejects_empty_source_file(self):
        with self.assertRaises(ValueError):
            questions_to_dict(
                [self.make_question()],
                source_file="",
            )