from __future__ import annotations

import pytest

from bhashanthara.datasets.fetch import DatasetFetchError, resolve_dataset_name


def test_resolve_dataset_name_maps_mmlu_alias() -> None:
    assert resolve_dataset_name("mmlu") == "cais/mmlu"


def test_resolve_dataset_name_accepts_explicit_dataset_name() -> None:
    assert resolve_dataset_name("org/dataset") == "org/dataset"


def test_resolve_dataset_name_rejects_empty_name() -> None:
    with pytest.raises(DatasetFetchError, match="cannot be empty"):
        resolve_dataset_name("  ")
