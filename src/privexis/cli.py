"""
Command-line interface for Privexis.
"""

import sys
from pathlib import Path
from typing import Optional

import typer

from .pipeline import (
    run_pipeline, scan_labelled, parse_metadata, metadata_template_csv,
    find_sources, load_config, load_checklist
)
from .report import write_all_reports


app = typer.Typer(help="Privexis: Personal-Data Discovery and Privacy Evidence Inventory")


@app.command()
def scan(
    data: str = typer.Option("data", "--data", "-d", help="Data directory or file"),
    config: str = typer.Option("config", "--config", "-c", help="Config directory"),
    labels: Optional[str] = typer.Option(None, "--labels", "-l", help="Labels CSV (for evaluation)"),
    holdout: Optional[str] = typer.Option(None, "--holdout", help="Holdout data directory"),
    out: str = typer.Option("reports", "--out", "-o", help="Output directory"),
    sample_size: int = typer.Option(50, "--sample-size", help="Max samples per column"),
    metadata_file: Optional[str] = typer.Option(None, "--metadata", "-m", help="Metadata CSV/YAML file"),
):
    """Scan data files for personal data and generate evidence reports."""
    data_path = Path(data)
    config_path = Path(config)
    out_path = Path(out)

    # Load configuration
    rules, scoring = load_config(str(config_path / "rules.yaml"))
    checklist = load_checklist(str(config_path / "checklist.yaml"))
    base_metadata = {}
    meta_path = config_path / "metadata.yaml"
    if meta_path.exists():
        import yaml
        with open(meta_path, encoding="utf-8") as f:
            base_metadata = yaml.safe_load(f).get("fields", {})

    # Load additional metadata from file if provided
    extra_metadata = {}
    if metadata_file:
        raw = Path(metadata_file).read_bytes()
        extra_metadata = parse_metadata(raw, metadata_file)

    # Merge metadata (extra overrides base)
    metadata = {**base_metadata, **extra_metadata}

    # Find source files
    if data_path.is_file():
        sources = [data_path]
    else:
        sources = find_sources(data_path)

    if not sources:
        typer.echo(f"No CSV or SQLite files found in {data}", err=True)
        raise typer.Exit(1)

    # Run pipeline
    typer.echo(f"Scanning {len(sources)} file(s)...")
    result = run_pipeline(sources, rules, scoring, metadata, checklist, sample_size)

    # Evaluate if labels provided
    metrics = {}
    holdout_metrics = None
    if labels and Path(labels).exists():
        from .evaluator import load_labels, evaluate
        truth = load_labels(labels)
        metrics = evaluate(result.findings, truth)
    else:
        # Default: evaluate against main labels if they exist
        default_labels = Path("data/labels.csv")
        if default_labels.exists():
            from .evaluator import load_labels, evaluate
            truth = load_labels(default_labels)
            metrics = evaluate(result.findings, truth)

    # Evaluate holdout if requested
    if holdout:
        holdout_path = Path(holdout)
        holdout_labels = holdout_path / "labels.csv"
        if holdout_labels.exists():
            _, holdout_metrics = scan_labelled(holdout_path, holdout_labels, rules, scoring)

    # Write reports
    out_path.mkdir(parents=True, exist_ok=True)
    write_all_reports(result, metrics, holdout_metrics, out_path, checklist)

    typer.echo(f"Done. Reports written to {out_path}")
    typer.echo(f"  Flagged: {len(result.findings)}")
    typer.echo(f"  Needs review: {len(result.review)}")
    if result.orphaned:
        typer.echo(f"  Orphaned metadata: {len(result.orphaned)}")


@app.command()
def template(
    output: str = typer.Option("metadata_template.csv", "--output", "-o", help="Output file"),
):
    """Generate a metadata CSV template."""
    Path(output).write_text(metadata_template_csv(), encoding="utf-8")
    typer.echo(f"Template written to {output}")


@app.command()
def version():
    """Show version."""
    typer.echo("Privexis 0.1.0")


def main(args: list[str] = None) -> int:
    """Entry point for `privexis` command."""
    if args is None:
        args = sys.argv[1:]
    try:
        app(args, standalone_mode=False)
        return 0
    except typer.Exit as e:
        return e.exit_code
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())