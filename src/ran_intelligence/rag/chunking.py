
"""Text cleaning and metadata-aware document chunking."""

import hashlib
import re
from typing import Any


def clean_text(text: str) -> str:
    """Normalize extracted PDF text without removing technical symbols."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.replace("\x00", " ")
    text = text.replace("\u00ad", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]*\n+", "\n\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    return text.strip()


def _split_long_text(text: str, chunk_size: int) -> list[str]:
    """Split long text while preferring sentence boundaries."""

    segments = []
    remaining = text.strip()

    while len(remaining) > chunk_size:
        window = remaining[:chunk_size + 1]

        boundaries = [
            window.rfind(". "),
            window.rfind("? "),
            window.rfind("! "),
            window.rfind("; "),
        ]

        split_at = max(boundaries)

        if split_at < chunk_size // 2:
            split_at = window.rfind(" ")

        if split_at < chunk_size // 2:
            split_at = chunk_size

        segment = remaining[:split_at].strip()

        if segment:
            segments.append(segment)

        remaining = remaining[split_at:].strip()

    if remaining:
        segments.append(remaining)

    return segments


def _build_chunks(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """Build overlapping chunks while preserving paragraph boundaries."""

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    segments = []

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            segments.extend(
                _split_long_text(paragraph, chunk_size)
            )
        else:
            segments.append(paragraph)

    chunks = []
    current = ""

    for segment in segments:
        candidate = (
            f"{current}\n\n{segment}"
            if current
            else segment
        )

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if overlap and current:
            prefix = current[-overlap:].strip()
            combined = f"{prefix}\n\n{segment}"

            if len(combined) <= chunk_size:
                current = combined
            else:
                current = segment
        else:
            current = segment

    if current:
        chunks.append(current)

    return chunks


def chunk_documents(
    documents: list[dict[str, Any]],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[dict[str, Any]]:
    """Clean and split extracted documents into metadata-rich chunks."""

    if chunk_size < 100:
        raise ValueError("chunk_size must be at least 100")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    chunks = []

    for document in documents:
        if "text" not in document:
            raise ValueError("Each document must contain text")

        metadata = document.get("metadata", {})
        text = clean_text(document["text"])

        if not text:
            continue

        text_chunks = _build_chunks(
            text,
            chunk_size,
            overlap,
        )

        for index, chunk_text in enumerate(text_chunks):
            source = str(metadata.get("source", "unknown"))
            page = metadata.get("page", 0)

            identifier = (
                f"{source}|{page}|{index}|{chunk_text}"
            )

            chunk_id = hashlib.sha256(
                identifier.encode("utf-8")
            ).hexdigest()[:16]

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": index,
                        "chunk_size": len(chunk_text),
                    },
                }
            )

    return chunks
