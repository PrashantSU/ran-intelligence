
import re
from typing import Any

CITATION_PATTERN = re.compile(r"\[S(\d+)\]")


def build_evidence_context(
    documents: list[dict[str, Any]],
    max_context_chars: int = 5000,
) -> tuple[str, list[dict[str, Any]]]:
    """Build a source-labelled evidence context within a character limit."""
    if not documents:
        raise ValueError("documents must not be empty")
    if max_context_chars < 1:
        raise ValueError("max_context_chars must be positive")

    items = []
    seed_positions = {}

    for position, document in enumerate(documents):
        text = str(document.get("text", "")).strip()
        if not text:
            continue

        source = document.get("source") or document.get("metadata", {}).get(
            "source", "unknown"
        )
        page = document.get("page")
        if page is None:
            page = document.get("metadata", {}).get("page", "unknown")

        chunk_index = document.get("chunk_index")
        if chunk_index is None:
            chunk_index = document.get("metadata", {}).get(
                "chunk_index", position
            )

        group = document.get("group", position)
        rank = document.get("rank", position + 1)

        item = {
            "text": text,
            "source": source,
            "page": page,
            "chunk_index": chunk_index,
            "chunk_id": document.get("chunk_id"),
            "group": group,
            "rank": rank,
            "position": position,
        }
        items.append(item)

        if document.get("is_seed", True):
            seed_positions.setdefault(group, position)

    def sort_key(item):
        seed_position = seed_positions.get(item["group"])
        if seed_position is not None and item["position"] > seed_position:
            return (1, item["rank"], item["position"])
        return (0, item["rank"], item["position"])

    items.sort(key=sort_key)

    context_parts = []
    sources = []
    seen_chunks = set()
    used_chars = 0

    for item in items:
        chunk_id = item["chunk_id"]
        if chunk_id is not None and chunk_id in seen_chunks:
            continue

        source_id = f"S{len(sources) + 1}"
        header = f"[{source_id}: {item['source']}, page {item['page']}]"
        passage = header + "\n" + item["text"]

        extra_chars = len(passage) + (2 if context_parts else 0)
        if used_chars + extra_chars > max_context_chars:
            continue

        context_parts.append(passage)
        sources.append({
            "id": source_id,
            "source_id": source_id,
            "source": item["source"],
            "page": item["page"],
            "pages": [item["page"]],
            "chunk_index": item["chunk_index"],
        })

        used_chars += extra_chars
        if chunk_id is not None:
            seen_chunks.add(chunk_id)

    if not context_parts:
        raise ValueError("No usable text found in the supplied documents")

    return "\n\n".join(context_parts), sources


def build_generation_prompt(query: str, evidence_context: str) -> str:
    """Build a complete, grounded telecom question-answering prompt."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")

    return f"""You are a technical assistant specialising in 4G and 5G NR.

Answer the question using only the supplied evidence.

Rules:
1. Do not add facts that are not supported by the evidence.
2. Review all evidence passages before composing your answer.
3. For list questions, identify every distinct item explicitly supported
   by the evidence. Do not omit items appearing in later passages or
   under separate headings.
4. Organise the answer using the categories and directions requested.
5. Distinguish physical channels, transport channels, logical channels,
   and physical signals. They are different categories.
6. When asked for physical channels, list only items explicitly
   identified as physical channels in the evidence.
7. Do not infer physical channels from mappings between logical and
   transport channels.
8. Cite each factual item using its supporting source, such as [S1].
9. Check that every relevant item found across the evidence appears
   in the answer.
10. If the evidence is incomplete or contradictory, explain the limitation.
11. Be concise, but never sacrifice completeness for brevity.

Evidence:
{evidence_context}

Question:
{query}

Answer:"""


def validate_answer_citations(
    answer: str,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate answer citations against the supplied evidence labels."""
    used_numbers = sorted({
        int(match) for match in CITATION_PATTERN.findall(answer or "")
    })

    available = set()
    for source in sources:
        source_id = source.get("source_id") or source.get("id", "")
        if (
            isinstance(source_id, str)
            and source_id.startswith("S")
            and source_id[1:].isdigit()
        ):
            available.add(int(source_id[1:]))

    invalid_numbers = sorted(set(used_numbers) - available)
    used = [f"S{number}" for number in used_numbers]
    invalid = [f"S{number}" for number in invalid_numbers]
    uncited = not used

    return {
        "valid": bool(used) and not invalid,
        "used": used,
        "invalid": invalid,
        "uncited": uncited,
        "used_sources": used,
        "invalid_sources": invalid,
    }


def generate_grounded_answer(
    query: str,
    documents: list[dict[str, Any]],
    tokenizer: Any,
    model: Any,
    device: str | None = None,
    max_input_tokens: int = 2048,
    max_new_tokens: int = 360,
    max_context_chars: int = 5000,
) -> dict[str, Any]:
    """Generate an answer grounded in retrieved telecom evidence."""
    import torch

    if not query or not query.strip():
        raise ValueError("query must not be empty")

    if not documents:
        return {
            "question": query,
            "answer": "Insufficient evidence to answer the question.",
            "sources": [],
            "citations": {
                "valid": False,
                "used": [],
                "invalid": [],
                "uncited": True,
                "used_sources": [],
                "invalid_sources": [],
            },
            "citation_validation": {
                "valid": False,
                "used": [],
                "invalid": [],
                "uncited": True,
                "used_sources": [],
                "invalid_sources": [],
            },
            "status": "insufficient_evidence",
            "model": None,
        }

    context, sources = build_evidence_context(
        documents,
        max_context_chars=max_context_chars,
    )
    prompt = build_generation_prompt(query, context)

    if getattr(tokenizer, "chat_template", None):
        model_input = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        )
        if hasattr(model_input, "input_ids"):
            input_ids = model_input.input_ids
            attention_mask = getattr(model_input, "attention_mask", None)
        else:
            input_ids = model_input
            attention_mask = None
    else:
        encoded = tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=True,
            truncation=False,
        )
        input_ids = encoded["input_ids"]
        attention_mask = encoded.get("attention_mask")

    input_token_count = input_ids.shape[-1]

    if input_token_count > max_input_tokens:
        raise ValueError(
            f"Input has {input_token_count} tokens, exceeding "
            f"the limit of {max_input_tokens}. "
            "Reduce the evidence context or increase the token limit."
        )

    if device is None:
        try:
            model_device = str(next(model.parameters()).device)
        except (AttributeError, StopIteration, TypeError):
            model_device = "cpu"
    else:
        model_device = device

    input_ids = input_ids.to(model_device)
    if attention_mask is not None:
        attention_mask = attention_mask.to(model_device)

    model.eval()

    generation_kwargs = {
        "input_ids": input_ids,
        "max_new_tokens": max_new_tokens,
        "do_sample": False,
        "pad_token_id": getattr(tokenizer, "pad_token_id", None),
        "eos_token_id": getattr(tokenizer, "eos_token_id", None),
    }
    if attention_mask is not None:
        generation_kwargs["attention_mask"] = attention_mask

    with torch.inference_mode():
        output = model.generate(**generation_kwargs)

    generated_tokens = output[0][input_token_count:]
    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()

    citation_result = validate_answer_citations(answer, sources)

    if citation_result["invalid"]:
        status = "invalid_citations"
    elif citation_result["uncited"]:
        status = "uncited"
    else:
        status = "answered"

    return {
        "question": query,
        "answer": answer,
        "sources": sources,
        "model": (
            getattr(getattr(model, "config", None), "_name_or_path", None)
            or getattr(model, "name_or_path", "unknown")
        ),
        "status": status,
        "citations": citation_result,
        "citation_validation": citation_result,
        "input_tokens": input_token_count,
    }
