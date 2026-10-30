"""
Main pipeline: orchestrates sampling -> scoring -> linking -> reporting.
Used by both CLI and web app.
"""

import csv
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .sampler import ColumnSample, find_sources, sample_path
from .engine import load_config, score_column, Rule, ScoringConfig, Finding
from .linker import load_checklist, load_metadata, link, orphaned_metadata, STATUS_COMPLETE, STATUS_GAP


@dataclass
class PipelineResult:
    """Complete result of a pipeline run."""
    findings: list[Finding] = field(default_factory=list)
    review: list[Finding] = field(default_factory=list)
    samples: dict[tuple[str, str, str], list[str]] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    orphaned: list[str] = field(default_factory=list)
    all_columns: list[Finding] = field(default_factory=list)

    @property
    def rows(self):
        return self.findings


def parse_metadata(raw: bytes, filename: str) -> dict:
    """
    Parse uploaded metadata from CSV or YAML.
    Returns dict keyed by "source:table:column".
    """
    if filename.lower().endswith((".yaml", ".yml")):
        data = yaml.safe_load(raw)
        return data.get("fields", {}) if isinstance(data, dict) else {}

    # CSV format: source,table,column,purpose,retention,owner
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    required_cols = {"source", "table", "column"}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        raise ValueError("CSV must have columns: source, table, column, [purpose, retention, owner]")

    meta = {}
    for row in reader:
        tbl = row['table'] if row.get('table') else "-"
        key = f"{row['source']}:{tbl}:{row['column']}"
        meta[key] = {k: v for k, v in row.items() if k not in required_cols and v}
    return meta


def metadata_template_csv() -> str:
    """Return a CSV template for metadata uploads."""
    return "source,table,column,purpose,retention,owner\ncustomers.csv,,email,Support,1 year,Ops\n"


def run_pipeline(
    paths: list[Path],
    rules: list[Rule],
    scoring: ScoringConfig,
    metadata: dict,
    checklist: dict,
    sample_size: int = 50,
) -> PipelineResult:
    """
    Run the full detection pipeline on a list of files.

    Args:
        paths: List of CSV/SQLite file paths
        rules: Detection rules from load_config()
        scoring: Scoring config from load_config()
        metadata: Declared metadata (from config/metadata.yaml or upload)
        checklist: Evidence checklist from load_checklist()
        sample_size: Max values to sample per column

    Returns:
        PipelineResult with findings, review list, samples, and orphaned metadata
    """
    all_samples: list[ColumnSample] = []
    samples_dict: dict[tuple[str, str, str], list[str]] = {}

    # 1. Sample all columns from all files
    for path in paths:
        cols = sample_path(path, k=sample_size)
        for c in cols:
            all_samples.append(c)
            samples_dict[(c.source, c.table, c.column)] = c.values

    # 2. Score each column
    scored: list[Finding] = []
    for sample in all_samples:
        finding = score_column(sample, rules, scoring)
        scored.append(finding)

    # 3. Link to metadata and evaluate checklist
    linked = link(scored, metadata, checklist)

    # 4. Split into flagged findings and review list
    findings = linked
    review = [f for f in scored if f.cls == "NONE" and f.confidence >= scoring.review_floor]

    # 5. Find orphaned metadata
    orphaned = orphaned_metadata(findings, metadata)

    return PipelineResult(
        findings=findings,
        review=review,
        samples=samples_dict,
        metadata=metadata,
        orphaned=orphaned,
        all_columns=scored,
    )


def scan_labelled(
    data_root: str | Path,
    labels_path: str | Path,
    rules: list[Rule],
    scoring: ScoringConfig,
) -> tuple[list[Finding], dict]:
    """
    Scan a labelled dataset and compute metrics.
    Used for evaluation on the holdout set.
    """
    from .evaluator import load_labels, evaluate

    data_root = Path(data_root)
    labels = load_labels(labels_path)
    sources = [s for s in find_sources(data_root) if s.name != "labels.csv"]
    checklist = load_checklist()

    result = run_pipeline(sources, rules, scoring, {}, checklist)
    metrics = evaluate(result.all_columns, labels)

    return result.all_columns, metrics