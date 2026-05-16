from __future__ import annotations

import json
from typing import Any

from bhashanthara.datasets.schema import TranslatedMCQItem, TranslationCandidate
from bhashanthara.models.openai_compatible import OpenAICompatibleClient
from bhashanthara.translate.generate import load_prompt
from bhashanthara.translate.json_utils import extract_json_object


def render_backtranslation_prompt(item: TranslatedMCQItem) -> str:
    payload = {
        "id": item.id,
        "question": item.question,
        "choices": item.choices,
        "answer_label": item.answer_label,
        "subject": item.subject,
        "domain": item.domain,
    }
    template = load_prompt("backtranslate_v1.txt")
    return template.format(input_json=json.dumps(payload, ensure_ascii=False, indent=2))


def backtranslate_item(
    item: TranslatedMCQItem,
    client: OpenAICompatibleClient,
) -> TranslationCandidate:
    response = client.complete(render_backtranslation_prompt(item))
    return TranslationCandidate.model_validate(extract_json_object(response.content))


def attach_backtranslation(
    item: TranslatedMCQItem,
    candidate: TranslationCandidate,
    model: str,
) -> TranslatedMCQItem:
    metadata = dict(item.metadata)
    translation = dict(metadata.get("translation") or {})
    translation["backtranslation"] = {
        "model": model,
        "question": candidate.question,
        "choices": candidate.choices,
        "notes": candidate.notes,
    }
    metadata["translation"] = translation
    return item.model_copy(update={"metadata": metadata})


def add_backtranslations(
    items: list[TranslatedMCQItem],
    client: OpenAICompatibleClient,
    limit: int | None = None,
) -> list[TranslatedMCQItem]:
    output: list[TranslatedMCQItem] = []
    for index, item in enumerate(items):
        if limit is not None and index >= limit:
            output.extend(items[index:])
            break
        candidate = backtranslate_item(item, client)
        output.append(attach_backtranslation(item, candidate, client.model))
    return output


def backtranslation_report(item: TranslatedMCQItem) -> dict[str, Any] | None:
    translation = item.metadata.get("translation")
    if not isinstance(translation, dict):
        return None
    backtranslation = translation.get("backtranslation")
    if not isinstance(backtranslation, dict):
        return None
    return {
        "id": item.id,
        "subject": item.subject,
        "domain": item.domain,
        "answer_label": item.answer_label,
        "question": backtranslation.get("question"),
        "choices": backtranslation.get("choices"),
        "model": backtranslation.get("model"),
        "notes": backtranslation.get("notes", ""),
    }
