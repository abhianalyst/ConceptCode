from unittest.mock import Mock

from django.test import SimpleTestCase

from question_generator.chunking.chunker import Chunk
from question_generator.generation.context import GenerationContext
from question_generator.generation.service import QuestionGenerationService
from question_generator.generation.topic_generator import (
    generate_questions_for_topic,
)
from question_generator.schemas import Question


class TopicGeneratorTests(SimpleTestCase):

    def make_question(self, difficulty, number):
        return Question(
            question=f"{difficulty} question {number}",
            options=[
                f"Correct {number}",
                f"Wrong A {number}",
                f"Wrong B {number}",
                f"Wrong C {number}",
            ],
            correct_answer=f"Correct {number}",
            explanation="Textbook explanation.",
            difficulty=difficulty,
            subject="Biology",
            chapter="Test Chapter",
            topic="Test Topic",
            source="biology_12.pdf",
        )

    def make_context(self):
        chunk = Chunk(
            chunk_id="test-chunk-1",
            text="Textbook material.",
            source="biology_12.pdf",
            page_start=1,
            page_end=1,
            subject="Biology",
            chapter="Test Chapter",
            topic="Test Topic",
        )

        return GenerationContext(
            subject="Biology",
            chapter="Test Chapter",
            topic="Test Topic",
            source="biology_12.pdf",
            chunks=[chunk],
        )

    def make_service(self):
        service = Mock(spec=QuestionGenerationService)

        calls = {
            "count": 0,
        }

        def generate(_context, *, difficulty=None):
            calls["count"] += 1
            batch_number = calls["count"]

            if difficulty is None:
                difficulties = [
                    "Easy",
                    "Medium",
                    "Hard",
                ]
            else:
                difficulties = [difficulty]

            return [
                self.make_question(
                    requested_difficulty,
                    batch_number * 100 + i,
                )
                for requested_difficulty in difficulties
                for i in range(8)
            ]

        service.generate.side_effect = generate

        return service

    def test_generates_exactly_60_questions(self):
        context = self.make_context()
        service = self.make_service()

        questions = generate_questions_for_topic(
            context,
            service,
        )

        self.assertEqual(len(questions), 60)

        difficulties = [
            question.difficulty
            for question in questions
        ]

        self.assertEqual(
            difficulties.count("Easy"),
            20,
        )
        self.assertEqual(
            difficulties.count("Medium"),
            20,
        )
        self.assertEqual(
            difficulties.count("Hard"),
            20,
        )

    def test_questions_are_grouped_by_difficulty(self):
        context = self.make_context()
        service = self.make_service()

        questions = generate_questions_for_topic(
            context,
            service,
        )

        self.assertTrue(
            all(
                question.difficulty == "Easy"
                for question in questions[:20]
            )
        )

        self.assertTrue(
            all(
                question.difficulty == "Medium"
                for question in questions[20:40]
            )
        )

        self.assertTrue(
            all(
                question.difficulty == "Hard"
                for question in questions[40:60]
            )
        )

    def test_requests_each_difficulty_explicitly(self):
        context = self.make_context()
        service = self.make_service()

        generate_questions_for_topic(
            context,
            service,
        )

        requested_difficulties = [
            call.kwargs["difficulty"]
            for call in service.generate.call_args_list
        ]

        self.assertTrue(
            all(
                difficulty == "Easy"
                for difficulty in requested_difficulties[:3]
            )
        )

        self.assertTrue(
            all(
                difficulty == "Medium"
                for difficulty in requested_difficulties[3:6]
            )
        )

        self.assertTrue(
            all(
                difficulty == "Hard"
                for difficulty in requested_difficulties[6:9]
            )
        )

    def test_duplicate_questions_are_removed(self):
        context = self.make_context()

        service = Mock(spec=QuestionGenerationService)

        question = self.make_question("Easy", 1)

        service.generate.return_value = [
            question,
            question,
        ]

        with self.assertRaises(ValueError):
            generate_questions_for_topic(
                context,
                service,
            )

    def test_wrong_difficulty_is_ignored(self):
        context = self.make_context()

        service = Mock(spec=QuestionGenerationService)

        calls = {
            "count": 0,
        }

        def generate(_context, *, difficulty=None):
            calls["count"] += 1
            batch_number = calls["count"]

            wrong_difficulty = {
                "Easy": "Medium",
                "Medium": "Hard",
                "Hard": "Easy",
            }[difficulty]

            correct_questions = [
                self.make_question(
                    difficulty,
                    batch_number * 100 + i,
                )
                for i in range(8)
            ]

            wrong_questions = [
                self.make_question(
                    wrong_difficulty,
                    batch_number * 1000 + i,
                )
                for i in range(2)
            ]

            return correct_questions + wrong_questions

        service.generate.side_effect = generate

        questions = generate_questions_for_topic(
            context,
            service,
        )

        self.assertEqual(len(questions), 60)

        self.assertEqual(
            sum(q.difficulty == "Easy" for q in questions),
            20,
        )
        self.assertEqual(
            sum(q.difficulty == "Medium" for q in questions),
            20,
        )
        self.assertEqual(
            sum(q.difficulty == "Hard" for q in questions),
            20,
        )

    def test_invalid_context_is_rejected(self):
        service = self.make_service()

        with self.assertRaises(TypeError):
            generate_questions_for_topic(
                "invalid",
                service,
            )

    def test_invalid_service_is_rejected(self):
        context = self.make_context()

        with self.assertRaises(TypeError):
            generate_questions_for_topic(
                context,
                "invalid",
            )