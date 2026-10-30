"""
Report generation: inventory CSV/JSON, gap report Markdown.
"""

import csv
import json
from pathlib import Path
from typing import Optional

from .engine import Finding
from .linker import STATUS_COMPLETE, STATUS_GAP
from .pipeline import PipelineResult


def write_inventory_csv(result: PipelineResult, out_dir: Path) -> Path:
    """Write inventory.csv with all flagged findings and their evidence."""
    path = out_dir / "inventory.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "source", "table", "column", "class", "confidence",
            "name_score", "value_score", "evidence",
            "purpose", "retention", "owner",
            "gaps", "review_status"
        ])
        for f in result.findings:
            meta = result.metadata.get(f"{f.source}:{f.table}:{f.column}", {})
            writer.writerow([
                f.source, f.table, f.column, f.cls, f.confidence,
                f.name_score, f.value_score, f.evidence,
                meta.get("purpose", ""), meta.get("retention", ""), meta.get("owner", ""),
                ";".join(f.gaps), f.review_status,
            ])
    return path


def write_inventory_json(result: PipelineResult, out_dir: Path) -> Path:
    """Write inventory.json with full detail."""
    path = out_dir / "inventory.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "findings": [
            {
                "source": f.source,
                "table": f.table,
                "column": f.column,
                "class": f.cls,
                "confidence": f.confidence,
                "name_score": f.name_score,
                "value_score": f.value_score,
                "evidence": f.evidence,
                "gaps": f.gaps,
                "review_status": f.review_status,
                "checklist": f.checklist,
            }
            for f in result.findings
        ],
        "review": [
            {
                "source": f.source,
                "table": f.table,
                "column": f.column,
                "confidence": f.confidence,
                "evidence": f.evidence,
            }
            for f in result.review
        ],
        "orphaned_metadata": result.orphaned,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def write_gap_report(result: PipelineResult, out_dir: Path, checklist: dict) -> Path:
    """Write gap_report.md with checklist table and gap summary."""
    path = out_dir / "gap_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Privexis Evidence Gap Report",
        "",
        "> **Disclaimer:** This report provides technical evidence for human review. "
        "It makes no legal or compliance determination. Every row is a *candidate* for "
        "review; nothing is called verified, compliant, or lawful.",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Flagged fields:** {len(result.findings)}",
        f"- **Needs review (below threshold):** {len(result.review)}",
        f"- **Orphaned metadata entries:** {len(result.orphaned)}",
        "",
        "## Checklist Table",
        "",
    ]

    # Build checklist table per class
    for cls in ("NAME", "EMAIL", "PHONE", "GOVT_ID", "DOB"):
        cls_findings = [f for f in result.findings if f.cls == cls]
        if not cls_findings:
            continue

        cls_checklist = checklist.get(cls, [])
        required_items = [c for c in cls_checklist if c["required"]]
        advisory_items = [c for c in cls_checklist if not c["required"]]

        lines.append(f"### {cls} ({len(cls_findings)} fields)")
        lines.append("")

        # Header
        headers = ["Column"] + [c["label"] for c in required_items] + [c["label"] for c in advisory_items] + ["Gaps", "Status"]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for finding in cls_findings:
            row = [f"`{finding.column}`"]
            for c in required_items:
                chk = next((x for x in finding.checklist if x["item"] == c["item"]), None)
                row.append("✓" if chk and chk["present"] else "✗")
            for c in advisory_items:
                chk = next((x for x in finding.checklist if x["item"] == c["item"]), None)
                row.append("✓" if chk and chk["present"] else "✗")
            row.append(", ".join(finding.gaps) if finding.gaps else "—")
            row.append(finding.review_status)
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")

    # Gap tally
    if result.findings:
        gap_counts: dict[str, int] = {}
        for f in result.findings:
            for g in f.gaps:
                gap_counts[g] = gap_counts.get(g, 0) + 1

        lines.append("## Gap Tally")
        lines.append("")
        for gap, count in sorted(gap_counts.items()):
            lines.append(f"- **{gap}**: {count}")
        lines.append("")

    # Orphaned metadata
    if result.orphaned:
        lines.append("## Orphaned Metadata")
        lines.append("")
        lines.append("These declared metadata entries have no matching detected field:")
        lines.append("")
        for key in result.orphaned:
            lines.append(f"- `{key}`")
        lines.append("")

    # Needs review
    if result.review:
        lines.append("## Needs a Closer Look")
        lines.append("")
        lines.append("Columns not flagged but with some evidence (above review floor, below threshold):")
        lines.append("")
        for f in result.review:
            lines.append(f"- `{f.column}` ({f.source}:{f.table}) — confidence {f.confidence:.2f}: {f.evidence}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated by Privexis. For audit use only.*")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def write_metrics_json(metrics: dict, out_dir: Path, name: str = "metrics.json") -> Path:
    """Write metrics JSON."""
    path = out_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    return path


def write_all_reports(
    result: PipelineResult,
    metrics: dict,
    holdout_metrics: Optional[dict],
    out_dir: Path,
    checklist: dict,
) -> list[Path]:
    """Write all report files to out_dir."""
    paths = []
    paths.append(write_inventory_csv(result, out_dir))
    paths.append(write_inventory_json(result, out_dir))
    paths.append(write_gap_report(result, out_dir, checklist))
    paths.append(write_metrics_json(metrics, out_dir, "metrics.json"))
    if holdout_metrics:
        paths.append(write_metrics_json(holdout_metrics, out_dir, "metrics_holdout.json"))
    return paths