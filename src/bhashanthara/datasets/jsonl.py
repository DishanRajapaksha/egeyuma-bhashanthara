from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from bhashanthara.datasets.schema import MCQItem, TranslatedMCQItem


class DatasetError(Exception):
    """Raised when a dataset cannot be read or validated."""


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise DatasetError(f"{path}:{line_number}: expected a JSON object")
            yield value


def load_mcq_jsonl(path: Path) -> list[MCQItem]:
    items: list[MCQItem] = []
    for line_number, raw in enumerate(read_jsonl(path), start=1):
        try:
            items.append(MCQItem.model_validate(raw))
        except ValidationError as exc:
            raise DatasetError(f"{path}:{line_number}: {exc}") from exc
    return items


def load_translated_jsonl(path: Path) -> list[TranslatedMCQItem]:
    items: list[TranslatedMCQItem] = []
    for line_number, raw in enumerate(read_jsonl(path), start=1):
        try:
            items.append(TranslatedMCQItem.model_validate(raw))
        except ValidationError as exc:
            raise DatasetError(f"{path}:{line_number}: {exc}") from exc
    return items


def write_jsonl(path: Path, items: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def append_jsonl(path: Path, items: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
