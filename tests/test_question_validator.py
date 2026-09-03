from django.test import SimpleTestCase

from question_generator.validation.validator import validate_question
from question_generator.schemas.question import Question


class QuestionValidatorTests(SimpleTestCase):

    def make_question(self, **overrides):
        data = {
            "question": "What is biotechnology?",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ],
            "correct_answer": "Option A",
            "explanation": "This is the explanation.",
            "difficulty": "Easy",
            "subject": "Biology",
            "chapter": "Biotechnology: Principles and Processes",
            "topic": "PRINCIPLES OF BIOTECHNOLOGY",
            "source": "biology_12.pdf",
        }
        data.update(overrides)
        return Question(**data)

    def test_valid_question_passes(self):
        question = self.make_question()

        validate_question(question)

    def test_duplicate_options_are_rejected(self):
        question = self.make_question(
            options=[
                "Option A",
                "Option A",
                "Option C",
                "Option D",
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "options must be unique",
        ):
            validate_question(question)

    def test_invalid_difficulty_is_rejected(self):
        question = self.make_question(difficulty="Very Hard")

        with self.assertRaisesRegex(
            ValueError,
            "difficulty must be Easy, Medium, or Hard",
        ):
            validate_question(question)

    def test_empty_explanation_is_rejected(self):
        question = self.make_question(explanation="")

        with self.assertRaisesRegex(
            ValueError,
            "explanation must be non-empty",
        ):
            validate_question(question)

    def test_empty_metadata_field_is_rejected(self):
        question = self.make_question(topic="")

        with self.assertRaisesRegex(
            ValueError,
            "topic must be non-empty",
        ):
            validate_question(question)

    def test_non_question_object_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_question("not a question")