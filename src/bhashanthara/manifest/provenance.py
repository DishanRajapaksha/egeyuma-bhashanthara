from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FileDigest:
    path: str
    sha256: str
    size_bytes: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    created_at: str
    source_files: list[FileDigest] = field(default_factory=list)
    output_files: list[FileDigest] = field(default_factory=list)
    prompt_files: list[FileDigest] = field(default_factory=list)
    models: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "source_files": [item.as_dict() for item in self.source_files],
            "output_files": [item.as_dict() for item in self.output_files],
            "prompt_files": [item.as_dict() for item in self.prompt_files],
            "models": self.models,
            "parameters": self.parameters,
            "notes": self.notes,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_digest(path: Path) -> FileDigest:
    return FileDigest(
        path=str(path),
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
    )


def utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_run_id(prefix: str) -> str:
    timestamp = utc_timestamp().replace(":", "").replace("-", "")
    return f"{prefix}_{timestamp}"


def create_manifest(
    *,
    run_id: str,
    source_files: list[Path],
    output_files: list[Path],
    prompt_files: list[Path] | None = None,
    models: dict[str, str] | None = None,
    parameters: dict[str, Any] | None = None,
    notes: str = "",
) -> RunManifest:
    return RunManifest(
        run_id=run_id,
        created_at=utc_timestamp(),
        source_files=[file_digest(path) for path in source_files],
        output_files=[file_digest(path) for path in output_files],
        prompt_files=[file_digest(path) for path in prompt_files or []],
        models=models or {},
        parameters=parameters or {},
        notes=notes,
    )
