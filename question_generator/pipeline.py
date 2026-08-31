import json
from pathlib import Path

from question_generator.pdf.extractor import extract_pdf


def pdf_to_json(
    pdf_path: str | Path,
    output_path: str | Path,
) -> Path:
    """
    Extract a PDF and save the structured representation as JSON.

    Args:
        pdf_path: Path to the source PDF.
        output_path: Path where the JSON file should be written.

    Returns:
        Path to the generated JSON file.
    """
    document = extract_pdf(pdf_path)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as file:
        json.dump(
            document.to_dict(),
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a PDF into structured JSON."
    )

    parser.add_argument(
        "pdf",
        help="Path to the input PDF.",
    )

    parser.add_argument(
        "output",
        help="Path to the output JSON file.",
    )

    args = parser.parse_args()

    result = pdf_to_json(
        pdf_path=args.pdf,
        output_path=args.output,
    )

    print(f"JSON written to: {result}")