from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.core.services.biology_question_generation import (
    generate_questions_from_biology_json,
)
from apps.core.services.llm_provider import (
    get_gemini_question_provider,
)
from question_generator.generation import (
    LLMQuestionGenerator,
    QuestionGenerationService,
)


class Command(BaseCommand):
    help = (
        "Generate Biology questions using Gemini."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--class-name",
            required=True,
            choices=[
                "class_11",
                "class_12",
            ],
            help="Biology class to generate questions for.",
        )

        parser.add_argument(
            "--chapter",
            required=True,
            type=int,
            help="Biology chapter number.",
        )

        parser.add_argument(
            "--output",
            required=True,
            help="Path for the generated JSON file.",
        )

    def handle(self, *args, **options):
        class_name = options["class_name"]
        chapter_number = options["chapter"]
        output_path = Path(options["output"])

        self.stdout.write(
            f"Generating Biology questions for "
            f"{class_name}, chapter {chapter_number}..."
        )

        try:
            provider = get_gemini_question_provider()

            generator = LLMQuestionGenerator(
                provider.generate
            )

            service = QuestionGenerationService(
                generator
            )

            result = generate_questions_from_biology_json(
                class_name,
                chapter_number,
                output_path,
                service=service,
            )

        except (ValueError, TypeError) as exc:
            raise CommandError(str(exc)) from exc

        except Exception as exc:
            raise CommandError(
                f"Question generation failed: {exc}"
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Biology question generation completed."
            )
        )

        self.stdout.write(
            f"Output: {result}"
        )