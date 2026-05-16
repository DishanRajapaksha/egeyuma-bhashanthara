from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bhashanthara.datasets.schema import (
    AnswerPreservationReview,
    MCQItem,
    SinhalaQualityReview,
    TranslatedMCQItem,
    TranslationRepairCandidate,
)
from bhashanthara.models.openai_compatible import OpenAICompatibleClient
from bhashanthara.translate.generate import load_prompt
from bhashanthara.translate.json_utils import extract_json_object

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def _review_payload(original: MCQItem, translated: TranslatedMCQItem) -> dict[str, Any]:
    return {
        "original": {
            "id": original.id,
            "question": original.question,
            "choices": original.choices,
            "answer_index": original.answer_index,
            "answer_label": original.answer_label,
            "subject": original.subject,
            "domain": original.domain,
        },
        "translated": {
            "id": translated.id,
            "question": translated.question,
            "choices": translated.choices,
            "answer_index": translated.answer_index,
            "answer_label": translated.answer_label,
        },
    }


def review_sinhala_quality(
    original: MCQItem,
    translated: TranslatedMCQItem,
    client: OpenAICompatibleClient,
) -> SinhalaQualityReview:
    template = load_prompt("review_sinhala_quality_v1.txt")
    prompt = template.format(
        input_json=json.dumps(_review_payload(original, translated), ensure_ascii=False, indent=2)
    )
    response = client.complete(prompt)
    return SinhalaQualityReview.model_validate(extract_json_object(response.content))


def review_answer_preservation(
    original: MCQItem,
    translated: TranslatedMCQItem,
    client: OpenAICompatibleClient,
) -> AnswerPreservationReview:
    template = load_prompt("review_answer_preservation_v1.txt")
    prompt = template.format(
        input_json=json.dumps(_review_payload(original, translated), ensure_ascii=False, indent=2)
    )
    response = client.complete(prompt)
    return AnswerPreservationReview.model_validate(extract_json_object(response.content))


def repair_translation(
    original: MCQItem,
    translated: TranslatedMCQItem,
    client: OpenAICompatibleClient,
) -> TranslationRepairCandidate:
    template = load_prompt("repair_translation_v1.txt")
    prompt = template.format(
        input_json=json.dumps(_review_payload(original, translated), ensure_ascii=False, indent=2)
    )
    response = client.complete(prompt)
    return TranslationRepairCandidate.model_validate(extract_json_object(response.content))
