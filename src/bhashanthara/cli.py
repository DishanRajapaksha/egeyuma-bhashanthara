from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from bhashanthara.datasets.jsonl import (
    DatasetError,
    load_mcq_jsonl,
    load_translated_jsonl,
    write_jsonl,
)
from bhashanthara.models.openai_compatible import OpenAICompatibleClient
from bhashanthara.translate.pipeline import translate_many, translate_verify_item

app = typer.Typer(help="Local-first Sinhala benchmark translation and verification pipeline.")
translate_app = typer.Typer(help="Translate and verify MCQ datasets.")
app.add_typer(translate_app, name="translate")
console = Console()


def _client(
    *,
    model: str,
    base_url: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> OpenAICompatibleClient:
    return OpenAICompatibleClient(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


@app.command()
def validate(input: Path) -> None:
    """Validate canonical MCQ JSONL input."""

    try:
        items = load_mcq_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Valid dataset[/green]: {input} ({len(items)} items)")


@translate_app.command("validate")
def validate_translated(input: Path) -> None:
    """Validate translated MCQ JSONL output."""

    try:
        items = load_translated_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid translated dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Valid translated dataset[/green]: {input} ({len(items)} items)")


@translate_app.command("generate")
def generate(
    input: Annotated[Path, typer.Option(help="Canonical English MCQ JSONL input.")],
    output: Annotated[Path, typer.Option(help="Translated Sinhala JSONL output.")],
    model: Annotated[str, typer.Option(help="Local/OpenAI-compatible translator model name.")],
    base_url: Annotated[
        str,
        typer.Option(help="OpenAI-compatible base URL."),
    ] = "http://localhost:1234/v1",
    api_key: Annotated[str, typer.Option(help="API key for the endpoint.")] = "local-key",
    temperature: Annotated[float, typer.Option(help="Sampling temperature.")] = 0.0,
    max_tokens: Annotated[int, typer.Option(help="Maximum generated tokens.")] = 2048,
    limit: Annotated[int | None, typer.Option(help="Optional item limit for pilots.")] = None,
) -> None:
    """Generate Bronze Sinhala translations using one model."""

    try:
        items = load_mcq_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    client = _client(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    translated = translate_many(items, client, limit=limit)
    write_jsonl(output, (item.model_dump() for item in translated))
    console.print(f"[green]Wrote[/green] {output} ({len(translated)} items)")


@translate_app.command("pipeline")
def pipeline(
    input: Annotated[Path, typer.Option(help="Canonical English MCQ JSONL input.")],
    output: Annotated[Path, typer.Option(help="Verified Sinhala JSONL output.")],
    translator: Annotated[str, typer.Option(help="Translator model name.")],
    sinhala_reviewer: Annotated[
        str | None,
        typer.Option(help="Optional Sinhala quality reviewer model."),
    ] = None,
    answer_reviewer: Annotated[
        str | None,
        typer.Option(help="Optional answer-preservation reviewer model."),
    ] = None,
    base_url: Annotated[
        str,
        typer.Option(help="OpenAI-compatible base URL."),
    ] = "http://localhost:1234/v1",
    api_key: Annotated[str, typer.Option(help="API key for the endpoint.")] = "local-key",
    temperature: Annotated[float, typer.Option(help="Sampling temperature.")] = 0.0,
    max_tokens: Annotated[int, typer.Option(help="Maximum generated tokens.")] = 2048,
    limit: Annotated[int | None, typer.Option(help="Optional item limit for pilots.")] = None,
) -> None:
    """Run translation plus optional LLM verification."""

    try:
        items = load_mcq_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    translator_client = _client(
        model=translator,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    sinhala_client = (
        _client(
            model=sinhala_reviewer,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if sinhala_reviewer
        else None
    )
    answer_client = (
        _client(
            model=answer_reviewer,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if answer_reviewer
        else None
    )

    translated = []
    for index, item in enumerate(items):
        if limit is not None and index >= limit:
            break
        console.print(f"Translating {index + 1}/{limit or len(items)}: {item.id}")
        translated.append(
            translate_verify_item(
                item,
                translator=translator_client,
                sinhala_reviewer=sinhala_client,
                answer_reviewer=answer_client,
            )
        )

    write_jsonl(output, (item.model_dump() for item in translated))
    console.print(f"[green]Wrote[/green] {output} ({len(translated)} items)")
