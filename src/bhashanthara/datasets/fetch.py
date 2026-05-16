from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download


class DatasetFetchError(Exception):
    """Raised when a dataset cannot be fetched."""


DEFAULT_DATASETS: dict[str, str] = {
    "mmlu": "cais/mmlu",
}


def resolve_dataset_name(name: str) -> str:
    normalised = name.strip()
    if not normalised:
        raise DatasetFetchError("dataset name cannot be empty")
    return DEFAULT_DATASETS.get(normalised.lower(), normalised)


def fetch_huggingface_dataset(
    *,
    dataset_name: str,
    output_dir: Path,
    revision: str | None = None,
    allow_patterns: list[str] | None = None,
) -> Path:
    repo_id = resolve_dataset_name(dataset_name)
    try:
        downloaded = snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            revision=revision,
            local_dir=output_dir,
            allow_patterns=allow_patterns,
        )
    except Exception as exc:  # pragma: no cover - network/provider errors vary.
        raise DatasetFetchError(f"failed to fetch dataset {repo_id}: {exc}") from exc
    return Path(downloaded)
