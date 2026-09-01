from django.test import SimpleTestCase

from question_generator.schemas import Question
from question_generator.validation.validator import (
    validate_question,
)


class QuestionValidatorTests(SimpleTestCase):

    def make_question(self, **overrides):
        data = {
            "question": "What carries genetic information?",
            "options": [
                "DNA",
                "RNA",
                "Protein",
                "Lipid",
            ],
            "correct_answer": "DNA",
            "explanation": "DNA carries genetic information.",
            "difficulty": "Easy",
            "subject": "Biology",
            "chapter": "Molecular Basis of Inheritance",
            "topic": "DNA",
            "source": "biology_12.pdf",
        }

        data.update(overrides)

        return Question(**data)

    def test_valid_question_is_returned(self):
        question = self.make_question()

        result = validate_question(question)

        self.assertIs(result, question)

    def test_rejects_non_question(self):
        with self.assertRaises(TypeError):
            validate_question("invalid")

    def test_rejects_duplicate_options(self):
        question = self.make_question(
            options=[
                "DNA",
                "RNA",
                "DNA",
                "Lipid",
            ]
        )

        with self.assertRaises(ValueError):
            validate_question(question)

    def test_rejects_empty_explanation(self):
        question = self.make_question(
            explanation="temporary",
        )

        # Question itself allows this, so validator must reject it.
        invalid = Question(
            question=question.question,
            options=question.options,
            correct_answer=question.correct_answer,
            explanation="",
            difficulty=question.difficulty,
            subject=question.subject,
            chapter=question.chapter,
            topic=question.topic,
            source=question.source,
        )

        with self.assertRaises(ValueError):
            validate_question(invalid)

    def test_rejects_invalid_difficulty(self):
        question = self.make_question(
            difficulty="Very Hard",
        )

        with self.assertRaises(ValueError):
            validate_question(question)

    def test_accepts_easy(self):
        self.assertIsNotNone(
            validate_question(
                self.make_question(difficulty="Easy")
            )
        )

    def test_accepts_medium(self):
        self.assertIsNotNone(
            validate_question(
                self.make_question(difficulty="Medium")
            )
        )

    def test_accepts_hard(self):
        self.assertIsNotNone(
            validate_question(
                self.make_question(difficulty="Hard")
            )
        )
