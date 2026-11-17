
"""PDF ingestion utilities for telecom RAG."""

from pathlib import Path
from typing import Any

import pymupdf


def extract_pdf(
    pdf_path: str | Path,
) -> list[dict[str, Any]]:
    """Extract text and metadata from each non-empty PDF page."""

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {path}")

    documents = []

    try:
        with pymupdf.open(path) as pdf:
            if pdf.is_encrypted:
                raise ValueError(f"Encrypted PDF: {path.name}")

            metadata = pdf.metadata or {}

            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                if not text:
                    continue

                documents.append(
                    {
                        "text": text,
                        "metadata": {
                            "source": path.name,
                            "source_path": str(path),
                            "page": page_number,
                            "total_pages": len(pdf),
                            "title": metadata.get("title") or path.stem,
                            "author": metadata.get("author") or "",
                            "subject": metadata.get("subject") or "",
                            "file_type": "pdf",
                        },
                    }
                )

    except pymupdf.FileDataError as exc:
        raise ValueError(
            f"Unable to read PDF: {path.name}"
        ) from exc

    if not documents:
        raise ValueError(
            f"No extractable text found in PDF: {path.name}"
        )

    return documents


def load_pdf_directory(
    directory: str | Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Load PDFs from a directory and report individual failures."""

    root = Path(directory)

    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(
            f"Invalid document directory: {root}"
        )

    documents = []
    failures = []

    pdf_files = sorted(root.rglob("*.pdf"))

    for pdf_path in pdf_files:
        try:
            documents.extend(extract_pdf(pdf_path))
        except (ValueError, OSError) as exc:
            failures.append(
                {
                    "file": str(pdf_path),
                    "error": str(exc),
                }
            )

    return documents, failures
