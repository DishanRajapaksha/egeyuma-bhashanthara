from __future__ import annotations

import json
from pathlib import Path

from bhashanthara.datasets.schema import (
    MCQItem,
    TranslatedMCQItem,
    TranslationCandidate,
    translated_item_from_candidate,
)
from bhashanthara.models.openai_compatible import OpenAICompatibleClient
from bhashanthara.translate.json_utils import extract_json_object

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def render_translation_prompt(item: MCQItem) -> str:
    payload = {
        "id": item.id,
        "question": item.question,
        "choices": item.choices,
        "answer_label": item.answer_label,
        "subject": item.subject,
        "domain": item.domain,
    }
    template = load_prompt("translate_mcq_si_v1.txt")
    return template.format(input_json=json.dumps(payload, ensure_ascii=False, indent=2))


def translate_item(item: MCQItem, client: OpenAICompatibleClient) -> TranslatedMCQItem:
    response = client.complete(render_translation_prompt(item))
    candidate = TranslationCandidate.model_validate(extract_json_object(response.content))
    return translated_item_from_candidate(
        original=item,
        candidate=candidate,
        translator_model=client.model,
    )
