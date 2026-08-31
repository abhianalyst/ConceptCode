from django.test import SimpleTestCase

from question_generator.schemas import Question


class QuestionSchemaTests(SimpleTestCase):

    def _make_question(self, **overrides):
        data = {
            "question": "What is DNA?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "DNA carries genetic information.",
            "difficulty": "Easy",
            "subject": "Biology",
            "chapter": "Biotechnology",
            "topic": "DNA",
            "source": "biology_12.pdf",
            "year_tag": None,
        }

        data.update(overrides)

        return Question(**data)

    def test_question_can_be_created(self):
        question = self._make_question()

        self.assertEqual(question.question, "What is DNA?")
        self.assertEqual(len(question.options), 4)
        self.assertEqual(question.correct_answer, "A")

    def test_to_dict_contains_expected_fields(self):
        question = self._make_question()

        data = question.to_dict()

        self.assertEqual(
            set(data),
            {
                "question",
                "options",
                "correct_answer",
                "explanation",
                "difficulty",
                "subject",
                "chapter",
                "topic",
                "source",
                "year_tag",
            },
        )

    def test_correct_answer_must_be_one_of_options(self):
        with self.assertRaises(ValueError):
            self._make_question(correct_answer="E")

    def test_exactly_four_options_are_required(self):
        with self.assertRaises(ValueError):
            self._make_question(options=["A", "B", "C"])

    def test_empty_question_is_rejected(self):
        with self.assertRaises(ValueError):
            self._make_question(question="")

    def test_empty_option_is_rejected(self):
        with self.assertRaises(ValueError):
            self._make_question(options=["A", "", "C", "D"])