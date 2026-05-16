from __future__ import annotations

from typing import Any

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.reports.stats import is_suspicious


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
