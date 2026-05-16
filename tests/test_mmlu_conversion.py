from __future__ import annotations

from pathlib import Path

import pytest

from bhashanthara.datasets.conversion.mmlu import (
    MMLUConversionError,
    convert_mmlu_csv,
    convert_mmlu_row,
)


def test_convert_mmlu_row_creates_mcq_item() -> None:
    item = convert_mmlu_row(
        [
            "Which gas is used by plants for photosynthesis?",
            "Oxygen",
            "Carbon dioxide",
            "Nitrogen",
            "Hydrogen",
            "B",
        ],
        row_number=1,
        subject="high_school_biology",
        domain="science",
        source="cais/mmlu",
        source_license="MIT",
        item_id="mmlu_high_school_biology_000001",
    )

    assert item.id == "mmlu_high_school_biology_000001"
    assert item.answer_index == 1
    assert item.answer_label == "B"
    assert item.metadata["mmlu_subject"] == "high_school_biology"
    assert item.metadata["mmlu_row_number"] == 1


def test_convert_mmlu_row_rejects_bad_column_count() -> None:
    with pytest.raises(MMLUConversionError, match="expected 6 columns"):
        convert_mmlu_row(
            ["Question", "A", "B"],
            row_number=1,
            subject="subject",
            domain=None,
            source="source",
            source_license="MIT",
            item_id="item_001",
        )


def test_convert_mmlu_csv_reads_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "Which gas is used by plants for photosynthesis?,"
        "Oxygen,Carbon dioxide,Nitrogen,Hydrogen,B\n"
        "What is the chemical formula of water?,CO2,H2O,O2,NaCl,B\n",
        encoding="utf-8",
    )

    items = convert_mmlu_csv(
        csv_path,
        subject="high_school_biology",
        domain="science",
    )

    assert len(items) == 2
    assert items[0].id == "mmlu_high_school_biology_000001"
    assert items[1].id == "mmlu_high_school_biology_000002"
