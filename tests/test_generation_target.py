from django.test import SimpleTestCase

from question_generator.generation.target import (
    QUESTIONS_PER_DIFFICULTY,
    TOTAL_QUESTIONS_PER_TOPIC,
    count_by_difficulty,
    is_target_reached,
)
from question_generator.schemas import Question


class GenerationTargetTests(SimpleTestCase):

    def make_question(self, difficulty, number):
        return Question(
            question=f"Question {difficulty} {number}",
            options=[
                "A",
                "B",
                "C",
                "D",
            ],
            correct_answer="A",
            explanation="Explanation.",
            difficulty=difficulty,
            subject="Biology",
            chapter="Test Chapter",
            topic="Test Topic",
            source="biology_12.pdf",
        )

    def test_counts_questions_by_difficulty(self):
        questions = [
            self.make_question("Easy", i)
            for i in range(3)
        ] + [
            self.make_question("Medium", i)
            for i in range(2)
        ] + [
            self.make_question("Hard", i)
            for i in range(1)
        ]

        self.assertEqual(
            count_by_difficulty(questions),
            {
                "Easy": 3,
                "Medium": 2,
                "Hard": 1,
            },
        )

    def test_target_is_not_reached_with_fewer_than_20_each(self):
        questions = [
            self.make_question("Easy", i)
            for i in range(20)
        ] + [
            self.make_question("Medium", i)
            for i in range(20)
        ] + [
            self.make_question("Hard", i)
            for i in range(19)
        ]

        self.assertFalse(
            is_target_reached(questions)
        )

    def test_target_is_reached_with_20_each(self):
        questions = [
            self.make_question(difficulty, i)
            for difficulty in (
                "Easy",
                "Medium",
                "Hard",
            )
            for i in range(20)
        ]

        self.assertTrue(
            is_target_reached(questions)
        )

        self.assertEqual(
            len(questions),
            TOTAL_QUESTIONS_PER_TOPIC,
        )

    def test_constants_match_requirement(self):
        self.assertEqual(
            QUESTIONS_PER_DIFFICULTY,
            20,
        )

        self.assertEqual(
            TOTAL_QUESTIONS_PER_TOPIC,
            60,
        )
