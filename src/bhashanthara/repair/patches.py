from __future__ import annotations

from typing import Any

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.reports.stats import is_suspicious


class RepairError(Exception):
    """Raised when a repair patch is invalid or cannot be applied."""


def export_repair_items(
    items: list[TranslatedMCQItem],
    suspicious_only: bool = True,
) -> list[dict[str, Any]]:
    selected = [item for item in items if is_suspicious(item)] if suspicious_only else items
    return [item_to_repair_record(item) for item in selected]


def item_to_repair_record(item: TranslatedMCQItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "question": item.question,
        "choices": item.choices,
        "answer_index": item.answer_index,
        "answer_label": item.answer_label,
        "subject": item.subject,
        "domain": item.domain,
        "source": item.source,
        "metadata": item.metadata,
        "repair": {
            "question": item.question,
            "choices": item.choices,
            "notes": "",
        },
    }


def _validate_repair_record(record: dict[str, Any]) -> tuple[str, str, list[str]]:
    item_id = record.get("id")
    if not isinstance(item_id, str) or not item_id:
        raise RepairError("repair record is missing a valid id")

    repair = record.get("repair")
    if not isinstance(repair, dict):
        raise RepairError(f"repair record {item_id} is missing repair object")

    question = repair.get("question")
    choices = repair.get("choices")
    if not isinstance(question, str) or not question.strip():
        raise RepairError(f"repair record {item_id} has an empty repair.question")
    if not isinstance(choices, list) or not all(isinstance(choice, str) for choice in choices):
        raise RepairError(f"repair record {item_id} has invalid repair.choices")
    if not choices or any(not choice.strip() for choice in choices):
        raise RepairError(f"repair record {item_id} has empty repair choices")

    return item_id, question, choices


def apply_repair_records(
    items: list[TranslatedMCQItem],
    repair_records: list[dict[str, Any]],
) -> list[TranslatedMCQItem]:
    repairs_by_id: dict[str, tuple[str, list[str], dict[str, Any]]] = {}
    for record in repair_records:
        item_id, question, choices = _validate_repair_record(record)
        repairs_by_id[item_id] = (question, choices, record)

    output: list[TranslatedMCQItem] = []
    for item in items:
        repair = repairs_by_id.get(item.id)
        if repair is None:
            output.append(item)
            continue

        question, choices, record = repair
        if len(choices) != len(item.choices):
            raise RepairError(
                f"repair record {item.id} changes choice count from "
                f"{len(item.choices)} to {len(choices)}"
            )

        metadata = dict(item.metadata)
        metadata["repair"] = {
            "status": "applied",
            "notes": _repair_notes(record),
        }

        translation = dict(metadata.get("translation") or {})
        translation["status"] = "needs_human_review"
        metadata["translation"] = translation

        output.append(
            item.model_copy(
                update={
                    "question": question,
                    "choices": choices,
                    "metadata": metadata,
                }
            )
        )
    return output


def _repair_notes(record: dict[str, Any]) -> str:
    repair = record.get("repair")
    if not isinstance(repair, dict):
        return ""
    notes = repair.get("notes")
    return str(notes or "")
