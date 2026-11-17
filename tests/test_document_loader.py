
import pymupdf
import pytest

from ran_intelligence.rag.document_loader import (
    extract_pdf,
    load_pdf_directory,
)


def create_test_pdf(path, pages):
    pdf = pymupdf.open()

    for content in pages:
        page = pdf.new_page()
        page.insert_text((72, 72), content)

    pdf.save(path)
    pdf.close()


def test_extract_pdf_preserves_page_metadata(tmp_path):
    path = tmp_path / "telecom.pdf"
    create_test_pdf(path, ["5G NR introduction", "Beamforming"])

    documents = extract_pdf(path)

    assert len(documents) == 2
    assert documents[0]["metadata"]["page"] == 1
    assert documents[1]["metadata"]["page"] == 2
    assert documents[0]["metadata"]["source"] == "telecom.pdf"
    assert "5G NR introduction" in documents[0]["text"]


def test_extract_pdf_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_pdf(tmp_path / "missing.pdf")


def test_extract_pdf_rejects_non_pdf(tmp_path):
    path = tmp_path / "document.txt"
    path.write_text("Not a PDF")

    with pytest.raises(ValueError):
        extract_pdf(path)


def test_extract_pdf_rejects_empty_pdf(tmp_path):
    path = tmp_path / "empty.pdf"
    create_test_pdf(path, [""])

    with pytest.raises(ValueError, match="No extractable text"):
        extract_pdf(path)


def test_load_pdf_directory(tmp_path):
    create_test_pdf(tmp_path / "first.pdf", ["RAN architecture"])
    create_test_pdf(tmp_path / "second.pdf", ["Radio resource management"])

    documents, failures = load_pdf_directory(tmp_path)

    assert len(documents) == 2
    assert failures == []


def test_load_pdf_directory_reports_failures(tmp_path):
    create_test_pdf(tmp_path / "valid.pdf", ["5G network"])
    (tmp_path / "invalid.pdf").write_text("Invalid PDF content")

    documents, failures = load_pdf_directory(tmp_path)

    assert len(documents) == 1
    assert len(failures) == 1
    assert failures[0]["file"].endswith("invalid.pdf")


def test_load_pdf_directory_rejects_invalid_directory(tmp_path):
    with pytest.raises(NotADirectoryError):
        load_pdf_directory(tmp_path / "missing")
