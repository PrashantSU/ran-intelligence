import re
from collections import defaultdict
from typing import Any

CITATION_PATTERN = re.compile(r"\[S(\d+)\]")





def build_evidence_context(
    documents: list[dict[str, Any]],
    max_context_chars: int = 5000,
) -> tuple[str, list[dict[str, Any]]]:
    """Prioritise all retrieval seeds before adjacent context chunks."""
    if max_context_chars < 1:
        raise ValueError("max_context_chars must be positive")

    candidates = []
    seed_positions = {}

    for position, document in enumerate(documents):
        metadata = document.get("metadata", {})
        rank = document.get("context_group_rank")
        if rank is None:
            rank = document.get("retrieval_rank")
        if rank is None:
            rank = 999999

        group = (metadata.get("source", "Unknown source"), rank)
        expanded = document.get("is_context_expansion", False)

        if not expanded:
            seed_positions[group] = position

        candidates.append({
            "document": document,
            "position": position,
            "group": group,
            "rank": rank,
            "expanded": expanded,
            "source": metadata.get("source", "Unknown source"),
            "page": metadata.get("page", "Unknown"),
            "chunk_index": metadata.get("chunk_index", position),
        })

    def priority(item):
        if not item["expanded"]:
            return (0, item["rank"], item["position"])

        seed_position = seed_positions.get(item["group"])

        if seed_position is not None and item["position"] > seed_position:
            return (1, item["rank"], item["position"])

        return (2, item["rank"], item["position"])

    candidates.sort(key=priority)

    context_parts = []
    sources = []
    used_chars = 0
    seen_chunks = set()

    for item in candidates:
        document = item["document"]
        chunk_id = document.get("chunk_id")

        if chunk_id is not None and chunk_id in seen_chunks:
            continue

        text = document.get("text", "").strip()
        if not text:
            continue

        source_id = f"S{len(sources) + 1}"
        header = f"[{source_id}: {item['source']}, page {item['page']}]"
        passage = header + chr(10) + text

        extra_chars = len(passage) + (2 if context_parts else 0)
        if used_chars + extra_chars > max_context_chars:
            continue

        context_parts.append(passage)
        sources.append({
            "source_id": source_id,
            "source": item["source"],
            "pages": [item["page"]],
            "chunk_index": item["chunk_index"],
        })
        used_chars += extra_chars

        if chunk_id is not None:
            seen_chunks.add(chunk_id)

    return (chr(10) * 2).join(context_parts), sources


def build_generation_prompt(
    query: str,
    evidence_context: str,
) -> str:
    """Build an exhaustive, grounded telecom question-answering prompt."""
    return f"""You are a technical assistant specialising in 4G and 5G NR.

Answer the question using only the supplied evidence.

Rules:
1. Do not introduce facts that are not supported by the evidence.
2. Review ALL evidence passages before composing your answer.
3. For list questions, identify EVERY distinct item explicitly supported
   by the evidence. Do not omit an item merely because it appears in a
   later passage or under a separate heading.
4. Organise the answer using the categories and directions requested.
5. Distinguish physical channels, transport channels, logical channels,
   and physical signals. They are different categories.
6. When asked for physical channels, list only items explicitly identified
   as physical channels in the evidence.
7. Do not infer physical channels from mappings between logical and
   transport channels.
8. Cite each factual item using its supporting source, such as [S1].
9. Before finalising, check that every relevant item found across ALL
   evidence passages appears in the answer.
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
    """Check whether citations refer to supplied evidence labels."""
    used = sorted(
        {int(match) for match in CITATION_PATTERN.findall(answer)}
    )
    available = {
        int(source["source_id"][1:])
        for source in sources
        if source.get("source_id", "").startswith("S")
        and source["source_id"][1:].isdigit()
    }

    invalid = sorted(set(used) - available)

    return {
        "valid": bool(used) and not invalid,
        "used_sources": [f"S{number}" for number in used],
        "invalid_sources": [f"S{number}" for number in invalid],
    }


def _count_input_tokens(tokenizer: Any, prompt: str) -> int:
    """Count prompt tokens without adding special tokens twice."""
    encoded = tokenizer(
        prompt,
        add_special_tokens=False,
        return_tensors="pt",
    )
    return encoded["input_ids"].shape[-1]


def generate_grounded_answer(
    query: str,
    documents: list[dict[str, Any]],
    tokenizer: Any,
    model: Any,
    device: str | None = None,
    max_input_tokens: int = 2048,
    max_new_tokens: int = 180,
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
            "status": "insufficient_evidence",
        }

    context, sources = build_evidence_context(
        documents,
        max_context_chars=max_context_chars,
    )

    if not context:
        return {
            "question": query,
            "answer": "Insufficient evidence to answer the question.",
            "sources": [],
            "status": "insufficient_evidence",
        }

    prompt = build_generation_prompt(query, context)

    if getattr(tokenizer, "chat_template", None):
        messages = [{"role": "user", "content": prompt}]
        model_input = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        )
        if hasattr(model_input, "input_ids"):
            input_ids = model_input["input_ids"]
            attention_mask = model_input.get("attention_mask")
            if attention_mask is None:
                attention_mask = torch.ones_like(input_ids)
        else:
            input_ids = model_input
            attention_mask = torch.ones_like(input_ids)
    else:
        encoded = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=False,
        )
        input_ids = encoded["input_ids"]
        attention_mask = encoded.get(
            "attention_mask",
            torch.ones_like(input_ids),
        )

    input_token_count = input_ids.shape[-1]

    if input_token_count > max_input_tokens:
        raise ValueError(
            f"Prompt contains {input_token_count} tokens, "
            f"exceeding the limit of {max_input_tokens}. "
            "Reduce the evidence context or increase the token limit."
        )

    model_device = (
        device
        if device is not None
        else str(next(model.parameters()).device)
    )

    input_ids = input_ids.to(model_device)
    attention_mask = attention_mask.to(model_device)

    model.eval()

    with torch.inference_mode():
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    # Decoder-only models return the prompt followed by generated tokens.
    generated_tokens = output[0, input_token_count:]
    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()

    citation_result = validate_answer_citations(answer, sources)

    status = (
        "answered"
        if citation_result["valid"]
        else "uncited"
    )

    return {
        "question": query,
        "answer": answer,
        "sources": sources,
        "model": getattr(model.config, "_name_or_path", "unknown"),
        "status": status,
        "citation_validation": citation_result,
        "input_tokens": input_token_count,
    }
