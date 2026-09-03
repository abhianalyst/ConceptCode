import json
from pathlib import Path

from django.test import SimpleTestCase

from question_generator.output import (
    export_topic_questions_json,
    questions_to_topic_dict,
)
from question_generator.schemas import Question


class TopicJsonExporterTests(SimpleTestCase):

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
            question=f"Question {number}",
            options=options,
            correct_answer=options[0],
            explanation="Explanation",
            difficulty=difficulty,
            subject="Biology",
            chapter="Biotechnology",
            topic=topic,
            source="biology_12.pdf",
        )

    def test_groups_questions_by_topic_and_difficulty(self):
        questions = [
            self.make_question(
                topic="Topic A",
                difficulty="Easy",
                number=1,
            ),
            self.make_question(
                topic="Topic A",
                difficulty="Hard",
                number=2,
            ),
            self.make_question(
                topic="Topic B",
                difficulty="Medium",
                number=3,
            ),
        ]

        data = questions_to_topic_dict(
            questions,
            source_file="biology_12.pdf",
        )

        self.assertEqual(
            data["chapter"],
            "Biotechnology",
        )

        self.assertEqual(
            [topic["topic"] for topic in data["topics"]],
            ["Topic A", "Topic B"],
        )

        topic_a = data["topics"][0]["questions"]

        self.assertEqual(len(topic_a["Easy"]), 1)
        self.assertEqual(len(topic_a["Medium"]), 0)
        self.assertEqual(len(topic_a["Hard"]), 1)

        topic_b = data["topics"][1]["questions"]

        self.assertEqual(len(topic_b["Easy"]), 0)
        self.assertEqual(len(topic_b["Medium"]), 1)
        self.assertEqual(len(topic_b["Hard"]), 0)

    def test_requires_single_chapter(self):
        questions = [
            self.make_question(
                topic="Topic A",
                difficulty="Easy",
                number=1,
            ),
            Question(
                question="Question 2",
                options=[
                    "A",
                    "B",
                    "C",
                    "D",
                ],
                correct_answer="A",
                explanation="Explanation",
                difficulty="Easy",
                subject="Biology",
                chapter="Different Chapter",
                topic="Topic B",
                source="biology_12.pdf",
            ),
        ]

        with self.assertRaises(ValueError):
            questions_to_topic_dict(
                questions,
                source_file="biology_12.pdf",
            )

    def test_invalid_difficulty_is_rejected(self):
        question = self.make_question(
            topic="Topic A",
            difficulty="Invalid",
            number=1,
        )

        with self.assertRaises(ValueError):
            questions_to_topic_dict(
                [question],
                source_file="biology_12.pdf",
            )

    def test_empty_questions_return_empty_topics(self):
        data = questions_to_topic_dict(
            [],
            source_file="biology_12.pdf",
        )

        self.assertEqual(data["chapter"], "")
        self.assertEqual(data["topics"], [])

    def test_export_writes_topic_json(self):
        questions = [
            self.make_question(
                topic="Topic A",
                difficulty="Easy",
                number=1,
            ),
        ]

        output = Path("tests") / "tmp_topic_questions.json"

        try:
            result = export_topic_questions_json(
                questions,
                output,
                source_file="biology_12.pdf",
            )

            self.assertEqual(result, output)
            self.assertTrue(output.exists())

            with output.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            self.assertEqual(
                data["chapter"],
                "Biotechnology",
            )
            self.assertEqual(
                data["topics"][0]["topic"],
                "Topic A",
            )
            self.assertEqual(
                len(
                    data["topics"][0]["questions"]["Easy"]
                ),
                1,
            )
        finally:
            if output.exists():
                output.unlink()