from pathlib import Path

import pymupdf

from question_generator.pdf.cleaner import clean_text
from question_generator.schemas.document import Document, Page, TextBlock


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be extracted successfully."""


def extract_pdf(pdf_path: str | Path) -> Document:
    """
    Extract text and text blocks from a PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A structured Document containing page and block information.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the supplied path is not a PDF.
        PDFExtractionError: If PyMuPDF cannot open or process the PDF.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if not path.is_file():
        raise ValueError(f"PDF path is not a file: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {path}")

    try:
        pdf = pymupdf.open(path)
    except Exception as exc:
        raise PDFExtractionError(
            f"Unable to open PDF: {path}"
        ) from exc

    try:
        pages: list[Page] = []

        for page_index, pdf_page in enumerate(pdf):
            raw_text = pdf_page.get_text("text")
            page_text = clean_text(raw_text)

            blocks: list[TextBlock] = []

            for block in pdf_page.get_text("blocks"):
                if len(block) < 5:
                    continue

                x0, y0, x1, y1, raw_block_text = block[:5]

                block_text = clean_text(raw_block_text)

                if not block_text:
                    continue

                blocks.append(
                    TextBlock(
                        text=block_text,
                        bbox=(
                            float(x0),
                            float(y0),
                            float(x1),
                            float(y1),
                        ),
                    )
                )

            pages.append(
                Page(
                    page_number=page_index + 1,
                    text=page_text,
                    blocks=blocks,
                )
            )

        metadata = pdf.metadata or {}
        title = metadata.get("title") or ""

        return Document(
            filename=path.name,
            title=title,
            page_count=len(pages),
            pages=pages,
        )

    except Exception as exc:
        raise PDFExtractionError(
            f"Failed while extracting PDF: {path}"
        ) from exc

    finally:
        pdf.close()