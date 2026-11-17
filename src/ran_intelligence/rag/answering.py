
import re
from typing import Any

CHANNEL_PATTERN = re.compile(
    r"Physical\s+"
    r"(?:(Downlink|Uplink)\s+)?"
    r"([A-Za-z][A-Za-z\s-]*?)\s+Channel\s*,\s*"
    r"([A-Z][A-Z0-9-]*)\b",
    re.IGNORECASE,
)

CHANNEL_DIRECTIONS = {
    "PDSCH": "downlink",
    "PDCCH": "downlink",
    "PBCH": "downlink",
    "PUSCH": "uplink",
    "PUCCH": "uplink",
    "PRACH": "uplink",
}

EXPECTED_CHANNELS = {
    "downlink": {"PDSCH", "PDCCH", "PBCH"},
    "uplink": {"PUSCH", "PUCCH", "PRACH"},
}

CHANNEL_ORDER = {
    "downlink": ("PDSCH", "PDCCH", "PBCH"),
    "uplink": ("PUSCH", "PUCCH", "PRACH"),
}


def extract_physical_channel_facts(
    documents: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Extract NR physical-channel definitions and preserve provenance."""
    if not documents:
        raise ValueError("documents must not be empty")

    facts = {"downlink": {}, "uplink": {}}

    for document in documents:
        text = document.get("text", "")
        metadata = document.get("metadata", {})

        if not text.strip():
            continue

        for match in CHANNEL_PATTERN.finditer(text):
            _, name, abbreviation = match.groups()
            abbreviation = abbreviation.upper()

            direction = CHANNEL_DIRECTIONS.get(abbreviation)

            if direction is None:
                continue

            name = " ".join(name.split()).strip()

            facts[direction][abbreviation] = {
                "name": f"Physical {name} Channel",
                "abbreviation": abbreviation,
                "source": metadata.get("source"),
                "page": metadata.get("page"),
            }

    return facts


def validate_physical_channel_facts(
    facts: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Check whether the expected NR channel inventory was found."""
    missing = {}

    for direction, expected in EXPECTED_CHANNELS.items():
        found = set(facts.get(direction, {}))
        missing[direction] = sorted(expected - found)

    complete = all(not channels for channels in missing.values())

    return {
        "valid": complete,
        "missing": missing,
        "found_counts": {
            direction: len(facts.get(direction, {}))
            for direction in EXPECTED_CHANNELS
        },
    }


def compose_physical_channel_answer(
    facts: dict[str, dict[str, dict[str, Any]]],
    validation: dict[str, Any],
) -> str:
    """Compose a cited answer only when evidence is complete."""
    if not validation["valid"]:
        raise ValueError(
            f"Incomplete channel evidence: {validation['missing']}"
        )

    lines = ["In NR, the physical channels are:", "", "Downlink:"]

    for abbreviation in CHANNEL_ORDER["downlink"]:
        item = facts["downlink"][abbreviation]
        lines.append(
            f"- {item['name']} ({abbreviation}) "
            f"[{item['source']}, PDF page {item['page']}]"
        )

    lines.extend(["", "Uplink:"])

    for abbreviation in CHANNEL_ORDER["uplink"]:
        item = facts["uplink"][abbreviation]
        lines.append(
            f"- {item['name']} ({abbreviation}) "
            f"[{item['source']}, PDF page {item['page']}]"
        )

    return "\n".join(lines)


def answer_physical_channels(
    question: str,
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    """Extract, validate and answer an NR physical-channel question."""
    if not question or not question.strip():
        raise ValueError("question must not be empty")

    facts = extract_physical_channel_facts(documents)
    validation = validate_physical_channel_facts(facts)

    answer = None

    if validation["valid"]:
        answer = compose_physical_channel_answer(facts, validation)

    sources = []
    seen = set()

    for direction in ("downlink", "uplink"):
        for abbreviation in CHANNEL_ORDER[direction]:
            item = facts[direction].get(abbreviation)

            if item is None:
                continue

            key = (item["source"], item["page"])

            if key not in seen:
                seen.add(key)
                sources.append({
                    "source": item["source"],
                    "page": item["page"],
                })

    return {
        "question": question,
        "answer": answer,
        "facts": facts,
        "sources": sources,
        "validation": validation,
        "status": "complete" if validation["valid"] else "incomplete",
    }
