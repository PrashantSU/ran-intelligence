"""Hugging Face adapter for structured investigation output."""

import json
import re
from collections.abc import Callable
from typing import Any

import torch


def _extract_json(text: str) -> dict[str, Any]:
    """Extract one JSON object from model output."""
    text = text.strip()

    # Remove common Markdown code fences.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start < 0 or end < start:
        raise ValueError("The model did not return a JSON object.")

    try:
        result = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError("The model returned invalid JSON.") from exc

    if not isinstance(result, dict):
        raise ValueError("The model output must be a JSON object.")

    return result


def create_huggingface_json_generator(
    model: Any,
    tokenizer: Any,
    max_new_tokens: int = 700,
) -> Callable[[str], dict[str, Any]]:
    """Create a deterministic JSON generator from a loaded HF model."""

    if max_new_tokens < 1:
        raise ValueError("max_new_tokens must be positive.")

    def generate(prompt: str) -> dict[str, Any]:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")

        if getattr(tokenizer, "chat_template", None):
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Return only valid JSON. Follow the requested schema "
                        "and do not include Markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ]
            inputs = tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            )
        else:
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
            )

        try:
            device = next(model.parameters()).device
        except (StopIteration, AttributeError):
            device = getattr(model, "device", "cpu")

        inputs = inputs.to(device)
        input_length = inputs["input_ids"].shape[-1]

        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id
                if tokenizer.pad_token_id is not None
                else tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        generated_tokens = output[0][input_length:]
        generated_text = tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        )

        return _extract_json(generated_text)

    return generate
