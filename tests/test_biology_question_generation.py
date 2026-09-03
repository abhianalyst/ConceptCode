from pathlib import Path
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from apps.core.services.biology_question_generation import (
    BIOLOGY_CHAPTER_TITLES,
    generate_questions_from_biology_json,
)
from question_generator.generation import QuestionGenerationService
from question_generator.schemas import Question


class BiologyQuestionGenerationTests(SimpleTestCase):

    def setUp(self):
        self.service = Mock(
            spec=QuestionGenerationService
        )

        self.question = Question(
            question="What is biotechnology?",
            options=[
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ],
            correct_answer="Option A",
            explanation="Explanation",
            difficulty="Easy",
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
            topic="PRINCIPLES OF BIOTECHNOLOGY",
            source="biology_12.pdf",
        )

        self.service.generate.return_value = [
            self.question
        ]

    def make_question(
        self,
        *,
        topic: str,
        difficulty: str,
        number: int,
    ) -> Question:
        options = [
            f"Option A {number}",
            f"Option B {number}",
            f"Option C {number}",
            f"Option D {number}",
        ]

        return Question(
            question=f"{difficulty} question {number}",
            options=options,
            correct_answer=options[0],
            explanation="Explanation",
            difficulty=difficulty,
            subject="Biology",
            chapter="Biotechnology: Principles and Processes",
            topic=topic,
            source="biology_12.pdf",
        )

    def make_generator(self):
        def generate(context, *, difficulty=None):
            return [
                self.make_question(
                    topic=context.topic,
                    difficulty=difficulty,
                    number=index,
                )
                for index in range(1, 21)
            ]

        self.service.generate.side_effect = generate

    def test_generates_questions_from_class_12_chapter_11(
        self,
    ):
        self.make_generator()

        output_path = Path(
            "tests/tmp_biology_questions.json"
        )

        with patch(
            "apps.core.services.biology_question_generation."
            "export_topic_questions_json"
        ) as mock_export:

            mock_export.return_value = output_path

            result = generate_questions_from_biology_json(
                "class_12",
                11,
                output_path,
                service=self.service,
            )

        self.assertEqual(
            result,
            output_path,
        )

        self.assertTrue(
            mock_export.called
        )

        exported_questions = (
            mock_export.call_args.args[0]
        )

        self.assertEqual(
            len(exported_questions),
            180,
        )

        topics = {
            question.topic
            for question in exported_questions
        }

        self.assertEqual(
            topics,
            {
                "PRINCIPLES OF BIOTECHNOLOGY",
                "TOOLS OF RECOMBINANT DNA TECHNOLOGY",
                "PROCESSES OF RECOMBINANT DNA TECHNOLOGY",
            },
        )

        for topic in topics:
            topic_questions = [
                question
                for question in exported_questions
                if question.topic == topic
            ]

            self.assertEqual(
                len(topic_questions),
                60,
            )

            for difficulty in (
                "Easy",
                "Medium",
                "Hard",
            ):
                difficulty_questions = [
                    question
                    for question in topic_questions
                    if question.difficulty == difficulty
                ]

                self.assertEqual(
                    len(difficulty_questions),
                    20,
                )

    def test_sections_are_generated_from_chapter_11(
        self,
    ):
        self.make_generator()

        output_path = Path(
            "tests/tmp_biology_questions.json"
        )

        with patch(
            "apps.core.services.biology_question_generation."
            "export_topic_questions_json"
        ):

            generate_questions_from_biology_json(
                "class_12",
                11,
                output_path,
                service=self.service,
            )

        self.assertEqual(
            self.service.generate.call_count,
            9,
        )

        contexts = [
            call.args[0]
            for call in self.service.generate.call_args_list
        ]

        topics = [
            context.topic
            for context in contexts
        ]

        self.assertEqual(
            topics,
            [
                "PRINCIPLES OF BIOTECHNOLOGY",
                "PRINCIPLES OF BIOTECHNOLOGY",
                "PRINCIPLES OF BIOTECHNOLOGY",
                "TOOLS OF RECOMBINANT DNA TECHNOLOGY",
                "TOOLS OF RECOMBINANT DNA TECHNOLOGY",
                "TOOLS OF RECOMBINANT DNA TECHNOLOGY",
                "PROCESSES OF RECOMBINANT DNA TECHNOLOGY",
                "PROCESSES OF RECOMBINANT DNA TECHNOLOGY",
                "PROCESSES OF RECOMBINANT DNA TECHNOLOGY",
            ],
        )

        requested_difficulties = [
            call.kwargs["difficulty"]
            for call in self.service.generate.call_args_list
        ]

        self.assertEqual(
            requested_difficulties,
            [
                "Easy",
                "Medium",
                "Hard",
                "Easy",
                "Medium",
                "Hard",
                "Easy",
                "Medium",
                "Hard",
            ],
        )

    def test_output_path_is_forwarded_to_exporter(
        self,
    ):
        self.make_generator()

        output_path = Path(
            "tests/custom_biology_output.json"
        )

        with patch(
            "apps.core.services.biology_question_generation."
            "export_topic_questions_json"
        ) as mock_export:

            mock_export.return_value = output_path

            result = generate_questions_from_biology_json(
                "class_12",
                11,
                output_path,
                service=self.service,
            )

        self.assertEqual(
            result,
            output_path,
        )

        mock_export.assert_called_once()

        self.assertEqual(
            mock_export.call_args.args[1],
            output_path,
        )

        self.assertEqual(
            mock_export.call_args.kwargs["source_file"],
            "biology_12.pdf",
        )

    def test_invalid_class_name_is_rejected(
        self,
    ):
        with self.assertRaises(ValueError):
            generate_questions_from_biology_json(
                "class_10",
                1,
                "output.json",
                service=self.service,
            )

    def test_invalid_chapter_number_is_rejected(
        self,
    ):
        with self.assertRaises(ValueError):
            generate_questions_from_biology_json(
                "class_12",
                99,
                "output.json",
                service=self.service,
            )

    def test_class_name_must_be_string(
        self,
    ):
        with self.assertRaises(ValueError):
            generate_questions_from_biology_json(
                12,
                1,
                "output.json",
                service=self.service,
            )

    def test_chapter_number_must_be_integer(
        self,
    ):
        with self.assertRaises(ValueError):
            generate_questions_from_biology_json(
                "class_12",
                "11",
                "output.json",
                service=self.service,
            )

    def test_service_must_be_generation_service(
        self,
    ):
        with self.assertRaises(TypeError):
            generate_questions_from_biology_json(
                "class_12",
                11,
                "output.json",
                service=Mock(),
            )

    def test_unknown_empty_sections_are_rejected(
        self,
    ):
        with patch(
            "apps.core.services.biology_question_generation."
            "extract_sections",
            return_value=[],
        ):
            with self.assertRaises(ValueError):
                generate_questions_from_biology_json(
                    "class_12",
                    11,
                    "output.json",
                    service=self.service,
                )

    def test_all_expected_biology_chapters_exist(
        self,
    ):
        self.assertEqual(
            len(BIOLOGY_CHAPTER_TITLES["class_11"]),
            22,
        )

        self.assertEqual(
            len(BIOLOGY_CHAPTER_TITLES["class_12"]),
            16,
        )