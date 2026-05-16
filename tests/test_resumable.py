from __future__ import annotations

from pathlib import Path

import pytest

from bhashanthara.datasets.jsonl import load_translated_jsonl
from bhashanthara.datasets.schema import MCQItem, TranslatedMCQItem
from bhashanthara.translate import resumable
from bhashanthara.translate.resumable import (
    PipelineFailure,
    completed_original_ids,
    original_id_from_translated,
    run_resumable_pipeline,
)


def item(item_id: str) -> MCQItem:
    return MCQItem(
        id=item_id,
        question="Question?",
        choices=["A", "B", "C", "D"],
        answer_index=1,
        answer_label="B",
    )


def translated(original_id: str) -> TranslatedMCQItem:
    return TranslatedMCQItem(
        id=f"{original_id}_si",
        question="ප්‍රශ්නය?",
        choices=["එක", "දෙක", "තුන", "හතර"],
        answer_index=1,
        answer_label="B",
        metadata={"original_id": original_id, "translation": {"status": "bronze"}},
    )


def test_original_id_from_translated_uses_metadata() -> None:
    assert original_id_from_translated(translated("item_001")) == "item_001"


def test_completed_original_ids_reads_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "out.jsonl"
    output.write_text(translated("item_001").model_dump_json() + "\n", encoding="utf-8")

    assert completed_original_ids(output) == {"item_001"}


def test_pipeline_failure_as_dict() -> None:
    failure = PipelineFailure(
        original_id="item_001",
        stage="pipeline",
        error_type="ValueError",
        error_message="bad json",
        item={"id": "item_001"},
    )

    assert failure.as_dict()["original_id"] == "item_001"
    assert failure.as_dict()["error_message"] == "bad json"


def test_run_resumable_pipeline_skips_completed_items(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    output = tmp_path / "out.jsonl"
    output.write_text(translated("item_001").model_dump_json() + "\n", encoding="utf-8")

    def fake_run_with_retries(*args: object, **kwargs: object) -> TranslatedMCQItem:
        return translated("item_002")

    monkeypatch.setattr(resumable, "run_with_retries", fake_run_with_retries)

    summary = run_resumable_pipeline(
        items=[item("item_001"), item("item_002")],
        output_path=output,
        translator=object(),  # type: ignore[arg-type]
        resume=True,
    )

    assert summary.considered == 2
    assert summary.skipped == 1
    assert summary.translated == 1
    assert [entry.id for entry in load_translated_jsonl(output)] == ["item_001_si", "item_002_si"]


def test_run_resumable_pipeline_logs_failures(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    output = tmp_path / "out.jsonl"
    failures = tmp_path / "failures.jsonl"

    def fake_run_with_retries(*args: object, **kwargs: object) -> TranslatedMCQItem:
        raise ValueError("bad model output")

    monkeypatch.setattr(resumable, "run_with_retries", fake_run_with_retries)

    summary = run_resumable_pipeline(
        items=[item("item_001")],
        output_path=output,
        translator=object(),  # type: ignore[arg-type]
        failures_output=failures,
        continue_on_error=True,
    )

    assert summary.failed == 1
    assert "bad model output" in failures.read_text(encoding="utf-8")


def test_run_resumable_pipeline_stops_without_continue_on_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output = tmp_path / "out.jsonl"

    def fake_run_with_retries(*args: object, **kwargs: object) -> TranslatedMCQItem:
        raise ValueError("bad model output")

    monkeypatch.setattr(resumable, "run_with_retries", fake_run_with_retries)

    with pytest.raises(ValueError, match="bad model output"):
        run_resumable_pipeline(
            items=[item("item_001")],
            output_path=output,
            translator=object(),  # type: ignore[arg-type]
        )
