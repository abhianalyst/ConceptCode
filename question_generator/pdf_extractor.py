from pathlib import Path

import pymupdf


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract text from every page of a PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text with page contents separated by blank lines.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"PDF path is not a file: {pdf_path}"
        )

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page in document:
            text = page.get_text("text")

            if text.strip():
                pages.append(text.strip())

    return "\n\n".join(pages)