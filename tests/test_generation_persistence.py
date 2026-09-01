from django.test import TestCase

from apps.core.models import Chapter, Subject, Topic
from question_generator.chunking import Chunk
from question_generator.generation import (
    GenerationContext,
    LLMQuestionGenerator,
    QuestionGenerationService,
)
from question_generator.persistence import save_questions
from question_generator.schemas import Question

class GenerationPersistenceTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(
            name="Biology",
        )

        self.chapter = Chapter.objects.create(
            subject=self.subject,
            unit_number=12,
            name="Molecular Basis of Inheritance",
        )

        self.topic = Topic.objects.create(
            chapter=self.chapter,
            name="DNA",
        )

        self.context = GenerationContext(
            subject="Biology",
            chapter="Molecular Basis of Inheritance",
            topic="DNA",
            source="biology_12.pdf",
            chunks=[
                Chunk(
                    chunk_id="test-1",
                    text="DNA carries genetic information.",
                    source="biology_12.pdf",
                    page_start=10,
                    page_end=10,
                    subject="Biology",
                    chapter="Molecular Basis of Inheritance",
                    topic="DNA",
                )
            ],
        )

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

    def test_generated_questions_can_be_persisted(self):
        question = self.make_question(
            "What carries genetic information?"
        )

        generator = LLMQuestionGenerator(
            lambda context: [question]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        saved_questions = save_questions(
            questions,
            topic=self.topic,
        )

        self.assertEqual(
            len(saved_questions),
            1,
        )

        saved = saved_questions[0]

        self.assertEqual(
            saved.topic,
            self.topic,
        )

        self.assertEqual(
            saved.question,
            "What carries genetic information?",
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

        self.assertEqual(
            saved.correct_answer,
            "DNA",
        )

        self.assertEqual(
            saved.difficulty,
            "Easy",
        )

        self.assertEqual(
            saved.source,
            "biology_12.pdf",
        )

    def test_generation_service_deduplicates_before_persistence(self):
        question1 = self.make_question(
            "What carries genetic information?"
        )

        question2 = self.make_question(
            "  WHAT   CARRIES genetic information?  "
        )

        generator = LLMQuestionGenerator(
            lambda context: [
                question1,
                question2,
            ]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        self.assertEqual(
            len(questions),
            1,
        )

        saved_questions = save_questions(
            questions,
            topic=self.topic,
        )

        self.assertEqual(
            len(saved_questions),
            1,
        )

        self.assertEqual(
            self.topic.questions.count(),
            1,
        )

    def test_persistence_preserves_question_fingerprint(self):
        question = self.make_question(
            "What carries genetic information?"
        )

        generator = LLMQuestionGenerator(
            lambda context: [question]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        saved = save_questions(
            questions,
            topic=self.topic,
        )[0]

        self.assertTrue(
            saved.question_fingerprint,
        )

        self.assertEqual(
            len(saved.question_fingerprint),
            64,
        )

    def test_duplicate_database_question_is_rejected(self):
        question = self.make_question(
            "What carries genetic information?"
        )

        generator = LLMQuestionGenerator(
            lambda context: [question]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        save_questions(
            questions,
            topic=self.topic,
        )

        with self.assertRaises(ValueError):
            save_questions(
                questions,
                topic=self.topic,
            )

        self.assertEqual(
            self.topic.questions.count(),
            1,
        )

    def test_multiple_generated_questions_are_persisted(self):
        question1 = self.make_question(
            "What carries genetic information?"
        )

        question2 = self.make_question(
            "Which molecule stores hereditary information?"
        )

        generator = LLMQuestionGenerator(
            lambda context: [
                question1,
                question2,
            ]
        )

        service = QuestionGenerationService(generator)

        questions = service.generate(self.context)

        self.assertEqual(
            len(questions),
            2,
        )

        saved_questions = save_questions(
            questions,
            topic=self.topic,
        )

        self.assertEqual(
            len(saved_questions),
            2,
        )

        self.assertEqual(
            self.topic.questions.count(),
            2,
        )
