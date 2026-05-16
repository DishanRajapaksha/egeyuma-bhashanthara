from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from bhashanthara.datasets.conversion.mmlu import MMLUConversionError, convert_mmlu_csv
from bhashanthara.datasets.jsonl import (
    DatasetError,
    load_mcq_jsonl,
    load_translated_jsonl,
    write_json,
    write_jsonl,
)
from bhashanthara.export.egeyuma import ExportStatus, export_egeyuma_items
from bhashanthara.models.openai_compatible import OpenAICompatibleClient
from bhashanthara.repair.patches import RepairError, apply_repair_records, export_repair_items
from bhashanthara.reports.stats import collect_translation_stats
from bhashanthara.review.labelstudio import (
    LABEL_CONFIG,
    apply_labelstudio_reviews,
    export_labelstudio_tasks,
)
from bhashanthara.translate.backtranslate import add_backtranslations, backtranslation_report
from bhashanthara.translate.pipeline import translate_many, translate_verify_item

app = typer.Typer(help="Local-first Sinhala benchmark translation and verification pipeline.")
datasets_app = typer.Typer(help="Convert external datasets into Bhashanthara MCQ JSONL.")
translate_app = typer.Typer(help="Translate and verify MCQ datasets.")
review_app = typer.Typer(help="Export and import human review tasks.")
repair_app = typer.Typer(help="Export and apply repaired translations.")
export_app = typer.Typer(help="Export datasets for downstream evaluation tools.")
app.add_typer(datasets_app, name="datasets")
app.add_typer(translate_app, name="translate")
app.add_typer(review_app, name="review")
app.add_typer(repair_app, name="repair")
app.add_typer(export_app, name="export")
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


@app.command()
def stats(
    input: Annotated[Path, typer.Option(help="Translated Sinhala JSONL input.")],
    output: Annotated[Path | None, typer.Option(help="Optional JSON report output.")] = None,
) -> None:
    """Show translation status and suspicious-item counts."""

    try:
        items = load_translated_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid translated dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    report = collect_translation_stats(items)
    table = Table(title="Bhashanthara translation stats")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("total", str(report.total))
    table.add_row("suspicious", str(report.suspicious_count))
    for status, count in report.by_status.items():
        table.add_row(f"status:{status}", str(count))
    console.print(table)

    if output is not None:
        write_json(output, report.as_dict())
        console.print(f"[green]Wrote[/green] {output}")


@datasets_app.command("convert-mmlu")
def convert_mmlu(
    input: Annotated[Path, typer.Option(help="MMLU CSV input: question,A,B,C,D,answer.")],
    output: Annotated[Path, typer.Option(help="Canonical MCQ JSONL output.")],
    subject: Annotated[str, typer.Option(help="MMLU subject name.")],
    domain: Annotated[str | None, typer.Option(help="Optional broad domain.")] = None,
    source: Annotated[str, typer.Option(help="Source dataset name.")] = "cais/mmlu",
    source_license: Annotated[str, typer.Option(help="Source dataset licence.")] = "MIT",
    id_prefix: Annotated[str | None, typer.Option(help="Optional item ID prefix.")] = None,
) -> None:
    """Convert an MMLU CSV file into canonical MCQ JSONL."""

    try:
        items = convert_mmlu_csv(
            input,
            subject=subject,
            domain=domain,
            source=source,
            source_license=source_license,
            id_prefix=id_prefix,
        )
    except MMLUConversionError as exc:
        console.print(f"[red]Invalid MMLU CSV:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    write_jsonl(output, (item.model_dump() for item in items))
    console.print(f"[green]Wrote[/green] {output} ({len(items)} items)")


@export_app.command("egeyuma")
def export_egeyuma(
    input: Annotated[Path, typer.Option(help="Translated Sinhala JSONL input.")],
    output: Annotated[Path, typer.Option(help="Egeyuma-compatible MCQ JSONL output.")],
    dataset_name: Annotated[str, typer.Option(help="Dataset name to write into exported items.")],
    min_status: Annotated[
        ExportStatus,
        typer.Option(help="Minimum translation status to export."),
    ] = "gold",
    language: Annotated[str, typer.Option(help="Exported language code.")] = "si",
) -> None:
    """Export translated items into Egeyuma-compatible MCQ JSONL."""

    try:
        items = load_translated_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid translated dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    exported = export_egeyuma_items(
        items,
        dataset_name=dataset_name,
        min_status=min_status,
        language=language,
    )
    write_jsonl(output, exported)
    console.print(f"[green]Wrote[/green] {output} ({len(exported)} items)")


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


@translate_app.command("backtranslate")
def backtranslate(
    input: Annotated[Path, typer.Option(help="Translated Sinhala JSONL input.")],
    output: Annotated[Path, typer.Option(help="Translated JSONL with backtranslation metadata.")],
    model: Annotated[str, typer.Option(help="Backtranslation model name.")],
    report_output: Annotated[
        Path | None,
        typer.Option(help="Optional JSON report of backtranslations."),
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
    """Backtranslate Sinhala items into English for drift inspection."""

    try:
        items = load_translated_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid translated dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    client = _client(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    updated = add_backtranslations(items, client, limit=limit)
    write_jsonl(output, (item.model_dump() for item in updated))
    console.print(f"[green]Wrote[/green] {output} ({len(updated)} items)")

    if report_output is not None:
        reports = [report for item in updated if (report := backtranslation_report(item))]
        write_json(report_output, {"backtranslations": reports})
        console.print(f"[green]Wrote[/green] {report_output} ({len(reports)} reports)")


@review_app.command("export-labelstudio")
def export_labelstudio(
    input: Annotated[Path, typer.Option(help="Translated Sinhala JSONL input.")],
    output: Annotated[Path, typer.Option(help="Label Studio task JSON output.")],
    include_all: Annotated[
        bool,
        typer.Option(help="Export all items instead of suspicious items only."),
    ] = False,
    label_config_output: Annotated[
        Path | None,
        typer.Option(help="Optional file path for Label Studio XML config."),
    ] = None,
) -> None:
    """Export translated items into Label Studio task JSON."""

    try:
        items = load_translated_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid translated dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    tasks = export_labelstudio_tasks(items, suspicious_only=not include_all)
    write_json(output, {"tasks": tasks})
    console.print(f"[green]Wrote[/green] {output} ({len(tasks)} tasks)")

    if label_config_output is not None:
        label_config_output.parent.mkdir(parents=True, exist_ok=True)
        label_config_output.write_text(LABEL_CONFIG, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {label_config_output}")


@review_app.command("import-labelstudio")
def import_labelstudio(
    input: Annotated[Path, typer.Option(help="Translated Sinhala JSONL input.")],
    labels: Annotated[Path, typer.Option(help="Label Studio exported task JSON.")],
    output: Annotated[Path, typer.Option(help="Reviewed translated JSONL output.")],
) -> None:
    """Import Label Studio decisions back into translated JSONL."""

    try:
        items = load_translated_jsonl(input)
        raw_labels = json.loads(labels.read_text(encoding="utf-8"))
    except (DatasetError, json.JSONDecodeError) as exc:
        console.print(f"[red]Invalid review import input:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if isinstance(raw_labels, dict) and isinstance(raw_labels.get("tasks"), list):
        tasks = raw_labels["tasks"]
    elif isinstance(raw_labels, list):
        tasks = raw_labels
    else:
        console.print("[red]Label Studio export must be a JSON list or an object with tasks.[/red]")
        raise typer.Exit(code=1)

    updated = apply_labelstudio_reviews(items, tasks)
    write_jsonl(output, (item.model_dump() for item in updated))
    console.print(f"[green]Wrote[/green] {output} ({len(updated)} items)")


@repair_app.command("export")
def export_repairs(
    input: Annotated[Path, typer.Option(help="Translated Sinhala JSONL input.")],
    output: Annotated[Path, typer.Option(help="Repair batch JSON output.")],
    include_all: Annotated[
        bool,
        typer.Option(help="Export all items instead of suspicious items only."),
    ] = False,
) -> None:
    """Export translated items into a repair batch JSON file."""

    try:
        items = load_translated_jsonl(input)
    except DatasetError as exc:
        console.print(f"[red]Invalid translated dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    repairs = export_repair_items(items, suspicious_only=not include_all)
    write_json(output, {"repairs": repairs})
    console.print(f"[green]Wrote[/green] {output} ({len(repairs)} repairs)")


@repair_app.command("apply")
def apply_repairs(
    input: Annotated[Path, typer.Option(help="Translated Sinhala JSONL input.")],
    repairs: Annotated[Path, typer.Option(help="Repair batch JSON input.")],
    output: Annotated[Path, typer.Option(help="Repaired translated JSONL output.")],
) -> None:
    """Apply repaired question and choice text back into translated JSONL."""

    try:
        items = load_translated_jsonl(input)
        raw_repairs = json.loads(repairs.read_text(encoding="utf-8"))
    except (DatasetError, json.JSONDecodeError) as exc:
        console.print(f"[red]Invalid repair input:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if isinstance(raw_repairs, dict) and isinstance(raw_repairs.get("repairs"), list):
        repair_records = raw_repairs["repairs"]
    elif isinstance(raw_repairs, list):
        repair_records = raw_repairs
    else:
        console.print("[red]Repair file must be a JSON list or an object with repairs.[/red]")
        raise typer.Exit(code=1)

    try:
        updated = apply_repair_records(items, repair_records)
    except RepairError as exc:
        console.print(f"[red]Invalid repair record:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    write_jsonl(output, (item.model_dump() for item in updated))
    console.print(f"[green]Wrote[/green] {output} ({len(updated)} items)")
