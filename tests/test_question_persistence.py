from django.test import TestCase

from apps.core.models import Chapter, Subject, Topic
from question_generator.persistence.questions import save_question
from question_generator.schemas import Question
from question_generator.validation.duplicate import (
    question_fingerprint,
)


class QuestionPersistenceTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(
            name="Biology",
        )

        self.chapter = Chapter.objects.create(
            subject=self.subject,
            unit_number=1,
            name="Molecular Basis of Inheritance",
        )

        self.topic = Topic.objects.create(
            chapter=self.chapter,
            name="DNA",
        )

        self.question = Question(
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

    def test_saves_question(self):
        saved = save_question(
            self.question,
            topic=self.topic,
        )

        self.assertIsNotNone(saved.pk)

        self.assertEqual(
            saved.question,
            self.question.question,
        )

    def test_maps_options_correctly(self):
        saved = save_question(
            self.question,
            topic=self.topic,
        )

        self.assertEqual(
            saved.option_a,
            "DNA",
        )

        self.assertEqual(
            saved.option_b,
            "RNA",
        )

        self.assertEqual(
            saved.option_c,
            "Protein",
        )

        self.assertEqual(
            saved.option_d,
            "Lipid",
        )

    def test_maps_question_metadata(self):
        saved = save_question(
            self.question,
            topic=self.topic,
        )

        self.assertEqual(
            saved.topic,
            self.topic,
        )

        self.assertEqual(
            saved.correct_answer,
            "DNA",
        )

        self.assertEqual(
            saved.explanation,
            "DNA carries genetic information.",
        )

        self.assertEqual(
            saved.difficulty,
            "Easy",
        )

        self.assertEqual(
            saved.source,
            "biology_12.pdf",
        )

    def test_generates_question_fingerprint(self):
        saved = save_question(
            self.question,
            topic=self.topic,
        )

        expected = question_fingerprint(
            self.question
        )

        self.assertEqual(
            saved.question_fingerprint,
            expected,
        )

        self.assertEqual(
            len(saved.question_fingerprint),
            64,
        )

    def test_rejects_duplicate_question(self):
        save_question(
            self.question,
            topic=self.topic,
        )

        duplicate = Question(
            question="  WHAT   CARRIES genetic information?  ",
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

        with self.assertRaises(ValueError):
            save_question(
                duplicate,
                topic=self.topic,
            )

    def test_rejects_invalid_question_type(self):
        with self.assertRaises(TypeError):
            save_question(
                "invalid",
                topic=self.topic,
            )

    def test_rejects_missing_topic(self):
        with self.assertRaises(ValueError):
            save_question(
                self.question,
                topic=None,
            )

    def test_saves_multiple_questions(self):
        question2 = Question(
            question="Which molecule contains genetic information?",
            options=[
                "DNA",
                "Glucose",
                "Lipid",
                "Water",
            ],
            correct_answer="DNA",
            explanation="DNA contains genetic information.",
            difficulty="Medium",
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
        )

        from question_generator.persistence.questions import (
            save_questions,
        )

        saved = save_questions(
            [
                self.question,
                question2,
            ],
            topic=self.topic,
        )

        self.assertEqual(len(saved), 2)

        self.assertEqual(
            self.topic.questions.count(),
            2,
        )

    def test_batch_rolls_back_on_duplicate(self):
        question2 = Question(
            question="Which molecule contains genetic information?",
            options=[
                "DNA",
                "Glucose",
                "Lipid",
                "Water",
            ],
            correct_answer="DNA",
            explanation="DNA contains genetic information.",
            difficulty="Medium",
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
        )

        from question_generator.persistence.questions import (
            save_questions,
        )

        save_question(
            self.question,
            topic=self.topic,
        )

        with self.assertRaises(ValueError):
            save_questions(
                [
                    question2,
                    self.question,
                ],
                topic=self.topic,
            )

        self.assertEqual(
            self.topic.questions.count(),
            1,
        )

        self.assertEqual(
            self.topic.questions.first().question,
            self.question.question,
        )

    def test_save_questions_rejects_non_list(self):
        from question_generator.persistence.questions import (
            save_questions,
        )

        with self.assertRaises(TypeError):
            save_questions(
                self.question,
                topic=self.topic,
            )