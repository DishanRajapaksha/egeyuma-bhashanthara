from __future__ import annotations

from pathlib import Path

from bhashanthara.manifest.provenance import (
    create_manifest,
    file_digest,
    sha256_file,
)


def test_sha256_file_returns_expected_digest(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")

    assert sha256_file(path) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_file_digest_includes_path_hash_and_size(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")

    digest = file_digest(path)

    assert digest.path == str(path)
    assert digest.size_bytes == 5
    assert digest.sha256 == sha256_file(path)


def test_create_manifest_collects_provenance(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    output = tmp_path / "output.jsonl"
    prompt = tmp_path / "prompt.txt"
    source.write_text("source", encoding="utf-8")
    output.write_text("output", encoding="utf-8")
    prompt.write_text("prompt", encoding="utf-8")

    manifest = create_manifest(
        run_id="test_run",
        source_files=[source],
        output_files=[output],
        prompt_files=[prompt],
        models={"translator": "qwen3-14b"},
        parameters={"limit": "200"},
        notes="Pilot run",
    ).as_dict()

    assert manifest["run_id"] == "test_run"
    assert manifest["source_files"][0]["sha256"] == sha256_file(source)
    assert manifest["output_files"][0]["sha256"] == sha256_file(output)
    assert manifest["prompt_files"][0]["sha256"] == sha256_file(prompt)
    assert manifest["models"] == {"translator": "qwen3-14b"}
    assert manifest["parameters"] == {"limit": "200"}
    assert manifest["notes"] == "Pilot run"
