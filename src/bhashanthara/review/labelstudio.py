from __future__ import annotations

from typing import Any

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.reports.stats import is_suspicious

REVIEW_METADATA_KEY = "human_review"


def item_to_labelstudio_task(item: TranslatedMCQItem) -> dict[str, Any]:
    metadata = item.metadata
    return {
        "data": {
            "id": item.id,
            "question": item.question,
            "choices": "\n".join(
                f"{chr(65 + index)}. {choice}" for index, choice in enumerate(item.choices)
            ),
            "answer_label": item.answer_label,
            "subject": item.subject or "unknown",
            "domain": item.domain or "unknown",
            "source": item.source or "unknown",
            "metadata": metadata,
        }
    }


def export_labelstudio_tasks(
    items: list[TranslatedMCQItem],
    suspicious_only: bool = True,
) -> list[dict[str, Any]]:
    selected = [item for item in items if is_suspicious(item)] if suspicious_only else items
    return [item_to_labelstudio_task(item) for item in selected]


def extract_task_id(task: dict[str, Any]) -> str | None:
    data = task.get("data")
    if not isinstance(data, dict):
        return None
    value = data.get("id")
    return str(value) if value else None


def choice_value(result: dict[str, Any]) -> str | None:
    value = result.get("value")
    if not isinstance(value, dict):
        return None
    choices = value.get("choices")
    if isinstance(choices, list) and choices:
        return str(choices[0])
    return None


def choice_values(result: dict[str, Any]) -> list[str]:
    value = result.get("value")
    if not isinstance(value, dict):
        return []
    choices = value.get("choices")
    if not isinstance(choices, list):
        return []
    return [str(choice) for choice in choices]


def text_value(result: dict[str, Any]) -> str:
    value = result.get("value")
    if not isinstance(value, dict):
        return ""
    texts = value.get("text")
    if isinstance(texts, list) and texts:
        return str(texts[0])
    return ""


def extract_review(task: dict[str, Any]) -> dict[str, Any] | None:
    annotations = task.get("annotations")
    if not isinstance(annotations, list) or not annotations:
        return None

    annotation = annotations[-1]
    results = annotation.get("result")
    if not isinstance(results, list):
        return None

    review: dict[str, Any] = {
        "decision": None,
        "failure_reasons": [],
        "notes": "",
        "labelstudio_annotation_id": annotation.get("id"),
    }

    for result in results:
        if not isinstance(result, dict):
            continue
        name = result.get("from_name")
        if name == "decision":
            review["decision"] = choice_value(result)
        elif name == "failure_reason":
            review["failure_reasons"] = choice_values(result)
        elif name == "notes":
            review["notes"] = text_value(result)

    if review["decision"] is None:
        return None
    return review


def status_from_decision(decision: str) -> str:
    if decision == "accept":
        return "gold"
    if decision == "reject":
        return "rejected"
    return "needs_human_review"


def apply_labelstudio_reviews(
    items: list[TranslatedMCQItem],
    labelstudio_tasks: list[dict[str, Any]],
) -> list[TranslatedMCQItem]:
    reviews_by_id: dict[str, dict[str, Any]] = {}
    for task in labelstudio_tasks:
        task_id = extract_task_id(task)
        review = extract_review(task)
        if task_id is not None and review is not None:
            reviews_by_id[task_id] = review

    updated: list[TranslatedMCQItem] = []
    for item in items:
        review = reviews_by_id.get(item.id)
        if review is None:
            updated.append(item)
            continue

        metadata = dict(item.metadata)
        metadata[REVIEW_METADATA_KEY] = review

        translation = dict(metadata.get("translation") or {})
        translation["status"] = status_from_decision(str(review["decision"]))
        metadata["translation"] = translation

        updated.append(item.model_copy(update={"metadata": metadata}))
    return updated


LABEL_CONFIG = """<View>
  <Header value="Sinhala translated MCQ"/>
  <Text name="question" value="$question"/>
  <Header value="Choices"/>
  <Text name="choices" value="$choices"/>
  <Header value="Expected answer"/>
  <Text name="answer" value="$answer_label"/>

  <Choices name="decision" toName="question" choice="single" required="true">
    <Choice value="accept"/>
    <Choice value="repair"/>
    <Choice value="reject"/>
    <Choice value="needs_human_review"/>
  </Choices>

  <Choices name="failure_reason" toName="question" choice="multiple">
    <Choice value="answer_changed"/>
    <Choice value="meaning_changed"/>
    <Choice value="ambiguous_question"/>
    <Choice value="duplicate_choices"/>
    <Choice value="bad_sinhala"/>
    <Choice value="domain_term_error"/>
    <Choice value="formatting_error"/>
  </Choices>

  <TextArea name="notes" toName="question" editable="true"/>
</View>
"""
