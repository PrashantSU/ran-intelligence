
import pytest

from ran_intelligence.rag.answering import (
    answer_physical_channels,
    extract_physical_channel_facts,
    validate_physical_channel_facts,
)


@pytest.fixture
def channel_documents():
    source = "3gpp-ts-38-211_v18.8.0.pdf"

    return [
        {
            "text": (
                "The following downlink physical channels are defined:\n"
                "- Physical Downlink Shared Channel, PDSCH\n"
                "- Physical Broadcast Channel, PBCH"
            ),
            "metadata": {"source": source, "page": 118},
        },
        {
            "text": (
                "- Physical Downlink Control Channel, PDCCH"
            ),
            "metadata": {"source": source, "page": 119},
        },
        {
            "text": (
                "The following uplink physical channels are defined:\n"
                "- Physical Uplink Shared Channel, PUSCH\n"
                "- Physical Uplink Control Channel, PUCCH\n"
                "- Physical Random Access Channel, PRACH"
            ),
            "metadata": {"source": source, "page": 33},
        },
    ]


def test_extracts_all_six_channels(channel_documents):
    facts = extract_physical_channel_facts(channel_documents)

    assert set(facts["downlink"]) == {"PDSCH", "PDCCH", "PBCH"}
    assert set(facts["uplink"]) == {"PUSCH", "PUCCH", "PRACH"}


def test_preserves_source_pages(channel_documents):
    facts = extract_physical_channel_facts(channel_documents)

    assert facts["downlink"]["PDSCH"]["page"] == 118
    assert facts["downlink"]["PDCCH"]["page"] == 119
    assert facts["uplink"]["PUSCH"]["page"] == 33


def test_complete_inventory_is_valid(channel_documents):
    facts = extract_physical_channel_facts(channel_documents)

    result = validate_physical_channel_facts(facts)

    assert result["valid"] is True
    assert result["missing"] == {
        "downlink": [],
        "uplink": [],
    }


def test_incomplete_inventory_is_rejected(channel_documents):
    facts = extract_physical_channel_facts(channel_documents[:2])

    result = validate_physical_channel_facts(facts)

    assert result["valid"] is False
    assert result["missing"]["uplink"] == [
        "PRACH", "PUCCH", "PUSCH"
    ]


def test_answer_contains_all_six_channels(channel_documents):
    result = answer_physical_channels(
        "Which physical channels are used for downlink and uplink in NR?",
        channel_documents,
    )

    assert result["status"] == "complete"

    for abbreviation in (
        "PDSCH", "PDCCH", "PBCH", "PUSCH", "PUCCH", "PRACH"
    ):
        assert abbreviation in result["answer"]


def test_incomplete_answer_is_not_composed(channel_documents):
    result = answer_physical_channels(
        "Which physical channels are used in NR?",
        channel_documents[:2],
    )

    assert result["status"] == "incomplete"
    assert result["answer"] is None


def test_empty_documents_rejected():
    with pytest.raises(ValueError, match="documents must not be empty"):
        extract_physical_channel_facts([])


def test_empty_question_rejected(channel_documents):
    with pytest.raises(ValueError, match="question must not be empty"):
        answer_physical_channels("", channel_documents)
