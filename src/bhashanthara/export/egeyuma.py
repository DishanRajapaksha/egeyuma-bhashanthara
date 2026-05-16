from __future__ import annotations

from enum import IntEnum
from typing import Any, Literal

from bhashanthara.datasets.schema import TranslatedMCQItem

ExportStatus = Literal["bronze", "silver", "gold"]


class StatusRank(IntEnum):
    BRONZE = 1
    SILVER = 2
    GOLD = 3


STATUS_RANKS: dict[str, StatusRank] = {
    "bronze": StatusRank.BRONZE,
    "silver": StatusRank.SILVER,
    "gold": StatusRank.GOLD,
}


def translation_status(item: TranslatedMCQItem) -> str:
    translation = item.metadata.get("translation")
    if not isinstance(translation, dict):
        return "unknown"
    return str(translation.get("status") or "unknown")


def should_export_item(item: TranslatedMCQItem, min_status: ExportStatus) -> bool:
    status = translation_status(item)
    rank = STATUS_RANKS.get(status)
    if rank is None:
        return False
    return rank >= STATUS_RANKS[min_status]


def to_egeyuma_item(
    item: TranslatedMCQItem,
    *,
    dataset_name: str,
    language: str = "si",
) -> dict[str, Any]:
    return {
        "id": item.id,
        "dataset": dataset_name,
        "task_type": "mcq",
        "language": language,
        "question": item.question,
        "choices": item.choices,
        "answer_index": item.answer_index,
        "answer_label": item.answer_label,
        "subject": item.subject,
        "category": item.domain,
        "source": item.source,
        "metadata": {
            **item.metadata,
            "exported_from": "egeyuma-bhashanthara",
            "export_schema": "egeyuma.mcq.v1",
        },
    }


def export_egeyuma_items(
    items: list[TranslatedMCQItem],
    *,
    dataset_name: str,
    min_status: ExportStatus = "gold",
    language: str = "si",
) -> list[dict[str, Any]]:
    return [
        to_egeyuma_item(item, dataset_name=dataset_name, language=language)
        for item in items
        if should_export_item(item, min_status)
    ]
