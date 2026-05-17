from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bhashanthara.datasets.jsonl import append_jsonl, load_translated_jsonl, write_jsonl
from bhashanthara.datasets.schema import MCQItem, TranslatedMCQItem
from bhashanthara.models.openai_compatible import OpenAICompatibleClient
from bhashanthara.translate.pipeline import translate_verify_item

ProgressCallback = Callable[[str], None]


@dataclass(frozen=True)
class PipelineFailure:
    original_id: str
    stage: str
    error_type: str
    error_message: str
    item: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class PipelineRunSummary:
    considered: int
    skipped: int
    translated: int
    failed: int


def original_id_from_translated(item: TranslatedMCQItem) -> str:
    original_id = item.metadata.get("original_id")
    if isinstance(original_id, str) and original_id:
        return original_id
    if item.id.endswith("_si"):
        return item.id.removesuffix("_si")
    return item.id


def completed_original_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()
    return {original_id_from_translated(item) for item in load_translated_jsonl(output_path)}


def failure_from_exception(
    item: MCQItem,
    exc: Exception,
    stage: str = "pipeline",
) -> PipelineFailure:
    return PipelineFailure(
        original_id=item.id,
        stage=stage,
        error_type=type(exc).__name__,
        error_message=str(exc),
        item=item.model_dump(),
    )


def run_with_retries(
    item: MCQItem,
    translator: OpenAICompatibleClient,
    repairer: OpenAICompatibleClient | None,
    sinhala_reviewer: OpenAICompatibleClient | None,
    answer_reviewer: OpenAICompatibleClient | None,
    max_retries: int,
) -> TranslatedMCQItem:
    last_error: Exception | None = None
    for _ in range(max_retries + 1):
        try:
            return translate_verify_item(
                item,
                translator=translator,
                repairer=repairer,
                sinhala_reviewer=sinhala_reviewer,
                answer_reviewer=answer_reviewer,
            )
        except Exception as exc:  # pragma: no cover
            last_error = exc
    if last_error is None:  # pragma: no cover
        raise RuntimeError("translation failed without an exception")
    raise last_error


def run_resumable_pipeline(
    *,
    items: list[MCQItem],
    output_path: Path,
    translator: OpenAICompatibleClient,
    repairer: OpenAICompatibleClient | None = None,
    sinhala_reviewer: OpenAICompatibleClient | None = None,
    answer_reviewer: OpenAICompatibleClient | None = None,
    failures_output: Path | None = None,
    resume: bool = False,
    continue_on_error: bool = False,
    max_retries: int = 0,
    limit: int | None = None,
    progress: ProgressCallback | None = None,
) -> PipelineRunSummary:
    selected = items[:limit] if limit is not None else items
    completed = completed_original_ids(output_path) if resume else set()
    if not resume:
        write_jsonl(output_path, [])
        if failures_output is not None:
            write_jsonl(failures_output, [])

    skipped = 0
    translated_count = 0
    failed = 0

    for index, item in enumerate(selected, start=1):
        if item.id in completed:
            skipped += 1
            if progress is not None:
                progress(f"Skipping {index}/{len(selected)}: {item.id}")
            continue

        if progress is not None:
            progress(f"Translating {index}/{len(selected)}: {item.id}")

        try:
            translated = run_with_retries(
                item,
                translator=translator,
                repairer=repairer,
                sinhala_reviewer=sinhala_reviewer,
                answer_reviewer=answer_reviewer,
                max_retries=max_retries,
            )
        except Exception as exc:
            failed += 1
            if failures_output is not None:
                failure = failure_from_exception(item, exc)
                append_jsonl(failures_output, [failure.as_dict()])
            if not continue_on_error:
                raise
            continue

        append_jsonl(output_path, [translated.model_dump()])
        translated_count += 1

    return PipelineRunSummary(len(selected), skipped, translated_count, failed)
