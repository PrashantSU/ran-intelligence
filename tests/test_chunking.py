
import pytest

from ran_intelligence.rag.chunking import (
    chunk_documents,
    clean_text,
)


def test_clean_text_normalizes_whitespace():
    text = "  5G   NR\nbeamforming\n\n\nresource allocation  "

    result = clean_text(text)

    assert result == "5G NR beamforming\n\nresource allocation"


def test_clean_text_preserves_technical_symbols():
    text = "SINR > 10 dB; RSRP = -95 dBm; 3GPP TS 38.214"

    assert clean_text(text) == text


def test_chunk_documents_preserves_metadata():
    documents = [
        {
            "text": "5G NR beamforming and resource scheduling.",
            "metadata": {
                "source": "3gpp.pdf",
                "page": 12,
            },
        }
    ]

    chunks = chunk_documents(documents, chunk_size=200)

    assert len(chunks) == 1
    assert chunks[0]["metadata"]["source"] == "3gpp.pdf"
    assert chunks[0]["metadata"]["page"] == 12
    assert chunks[0]["metadata"]["chunk_index"] == 0


def test_chunk_documents_respects_chunk_size():
    text = " ".join(["telecom engineering"] * 100)

    chunks = chunk_documents(
        [{"text": text, "metadata": {"source": "test.pdf"}}],
        chunk_size=200,
        overlap=20,
    )

    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= 200 for chunk in chunks)


def test_chunk_documents_generates_stable_ids():
    document = [
        {
            "text": "5G NR scheduling.",
            "metadata": {"source": "test.pdf", "page": 1},
        }
    ]

    first = chunk_documents(document)
    second = chunk_documents(document)

    assert first[0]["chunk_id"] == second[0]["chunk_id"]


def test_chunk_documents_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_documents([], chunk_size=200, overlap=200)


def test_chunk_documents_rejects_missing_text():
    with pytest.raises(ValueError):
        chunk_documents([{"metadata": {}}])


def test_chunk_documents_skips_empty_text():
    chunks = chunk_documents(
        [{"text": "   ", "metadata": {"source": "empty.pdf"}}]
    )

    assert chunks == []


def test_chunk_documents_preserves_technical_content():
    text = (
        "SINR = 18 dB; RSRP = -95 dBm. "
        "NR uses 64 antennas for coordinated beamforming."
    )

    chunks = chunk_documents(
        [{"text": text, "metadata": {"source": "radio.pdf"}}],
        chunk_size=200,
    )

    assert "SINR = 18 dB" in chunks[0]["text"]
    assert "64 antennas" in chunks[0]["text"]
