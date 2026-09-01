from django.test import SimpleTestCase

from question_generator.schemas import Question
from question_generator.validation.duplicate import (
    filter_duplicates,
    normalize_question_text,
    question_fingerprint,
)


class QuestionDuplicateTests(SimpleTestCase):

    def make_question(self, text):
        return Question(
            question=text,
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

    def test_normalize_question_text(self):
        result = normalize_question_text(
            "  What   is   DNA?  "
        )

        self.assertEqual(
            result,
            "what is dna?",
        )

    def test_normalization_is_case_insensitive(self):
        self.assertEqual(
            normalize_question_text("WHAT IS DNA?"),
            normalize_question_text("what is dna?"),
        )

    def test_normalization_collapses_whitespace(self):
        self.assertEqual(
            normalize_question_text(
                "What    is\nDNA?"
            ),
            "what is dna?",
        )

    def test_fingerprint_is_stable(self):
        question = self.make_question("What is DNA?")

        self.assertEqual(
            question_fingerprint(question),
            question_fingerprint(question),
        )

    def test_equivalent_questions_have_same_fingerprint(self):
        first = self.make_question("What is DNA?")
        second = self.make_question("  WHAT   IS   DNA? ")

        self.assertEqual(
            question_fingerprint(first),
            question_fingerprint(second),
        )

    def test_different_questions_have_different_fingerprints(self):
        first = self.make_question("What is DNA?")
        second = self.make_question("What carries genetic information?")

        self.assertNotEqual(
            question_fingerprint(first),
            question_fingerprint(second),
        )

    def test_filter_duplicates_keeps_first_question(self):
        first = self.make_question("What is DNA?")
        duplicate = self.make_question("  WHAT   IS   DNA? ")
        third = self.make_question(
            "What carries genetic information?"
        )

        result = filter_duplicates(
            [first, duplicate, third]
        )

        self.assertEqual(
            result,
            [first, third],
        )

    def test_filter_duplicates_empty_list(self):
        self.assertEqual(
            filter_duplicates([]),
            [],
        )

    def test_filter_duplicates_rejects_invalid_input(self):
        with self.assertRaises(TypeError):
            filter_duplicates("invalid")

    def test_filter_duplicates_rejects_invalid_question(self):
        with self.assertRaises(TypeError):
            filter_duplicates(
                [self.make_question("Valid?"), "invalid"]
            )
