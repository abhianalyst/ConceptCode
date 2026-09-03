import argparse
import logging
from pathlib import Path

from question_generator.generation import (
    generate_questions_from_sections,
)
from question_generator.output import export_questions_json
from question_generator.pdf.extractor import extract_pdf
from question_generator.sections import extract_sections


logger = logging.getLogger(__name__)


def generate_questions_from_pdf(
    pdf_path: str | Path,
    output_path: str | Path,
    *,
    subject: str,
    chapter: str,
) -> Path:
    """
    Generate questions from a textbook PDF and export them as JSON.

    Pipeline:

        PDF
        -> extraction
        -> section extraction
        -> generation
        -> validation
        -> deduplication
        -> JSON export
    """

    if not isinstance(subject, str) or not subject.strip():
        raise ValueError(
            "subject must be a non-empty string"
        )

    if not isinstance(chapter, str) or not chapter.strip():
        raise ValueError(
            "chapter must be a non-empty string"
        )

    pdf_path = Path(pdf_path)

    logger.info(
        "Extracting PDF: %s",
        pdf_path,
    )

    document = extract_pdf(pdf_path)

    logger.info(
        "PDF extracted: %d pages",
        document.page_count,
    )

    pages = [
        page.to_dict()
        for page in document.pages
    ]

    logger.info(
        "Extracting sections from chapter: %s",
        chapter,
    )

    sections = extract_sections(
        pages,
        source=document.filename,
        chapter=chapter,
        subject=subject,
    )

    if not sections:
        raise ValueError(
            f"No sections found in PDF: {pdf_path}"
        )

    logger.info(
        "Found %d sections",
        len(sections),
    )

    from apps.core.services.question_generation import (
        get_question_generation_service,
    )

    service = get_question_generation_service()

    logger.info(
        "Generating questions",
    )

    questions = generate_questions_from_sections(
        sections,
        subject=subject,
        source=document.filename,
        service=service,
    )

    logger.info(
        "Generated %d questions",
        len(questions),
    )

    output = export_questions_json(
        questions,
        output_path,
        source_file=document.filename,
    )

    logger.info(
        "Questions exported: %s",
        output,
    )

    return output


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate educational questions "
            "from a textbook PDF."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input PDF.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output JSON file.",
    )

    parser.add_argument(
        "--subject",
        required=True,
        help="Subject name, for example Biology.",
    )

    parser.add_argument(
        "--chapter",
        required=True,
        help="Chapter name represented by the PDF input.",
    )

    return parser


def main() -> int:
    """Run the question-generation CLI."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    parser = build_parser()
    args = parser.parse_args()

    try:
        output = generate_questions_from_pdf(
            pdf_path=args.input,
            output_path=args.output,
            subject=args.subject,
            chapter=args.chapter,
        )
    except Exception as exc:
        logger.error("%s", exc)
        return 1

    print(f"Questions written to: {output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())