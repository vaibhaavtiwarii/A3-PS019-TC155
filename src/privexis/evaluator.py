"""
Evaluation: compares scanner findings against hand-labelled truth sets.
Computes per-class precision, recall, and F1.
"""

import csv
from pathlib import Path
from typing import Optional

from .engine import Finding

# All known PII classes
CLASSES = ("NAME", "EMAIL", "PHONE", "GOVT_ID", "DOB")


def load_labels(path: str | Path = "data/labels.csv") -> dict[tuple[str, str, str], str]:
    """
    Load hand-labelled truth from CSV.
    Returns dict keyed by (source, table, column) -> class.
    """
    path = Path(path)
    truth: dict[tuple[str, str, str], str] = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["source"], row["table"], row["column"])
            cls = (row.get("class") or row.get("true_class") or "NONE").upper()
            truth[key] = cls

    return truth


def evaluate(
    findings: list[Finding],
    truth: dict[tuple[str, str, str], str],
) -> dict:
    """
    Compare findings against truth labels.
    Returns metrics dict with per-class and overall stats.
    """
    # Build finding lookup
    found = {(f.source, f.table, f.column): f.cls for f in findings}

    # All columns that appear in either set
    all_keys = set(found.keys()) | set(truth.keys())

    # Per-class counts
    per_class: dict[str, dict] = {}
    for cls in CLASSES:
        tp = fp = fn = 0
        for key in all_keys:
            true_cls = truth.get(key, "NONE")
            pred_cls = found.get(key, "NONE")
            if true_cls == cls and pred_cls == cls:
                tp += 1
            elif true_cls != cls and pred_cls == cls:
                fp += 1
            elif true_cls == cls and pred_cls != cls:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else None
        recall = tp / (tp + fn) if (tp + fn) > 0 else None
        f1 = (2 * precision * recall / (precision + recall)) if precision and recall and (precision + recall) > 0 else None

        per_class[cls] = {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(precision, 4) if precision is not None else None,
            "recall": round(recall, 4) if recall is not None else None,
            "f1": round(f1, 4) if f1 is not None else None,
        }

    # Overall (micro-average)
    total_tp = sum(v["tp"] for v in per_class.values())
    total_fp = sum(v["fp"] for v in per_class.values())
    total_fn = sum(v["fn"] for v in per_class.values())
    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    overall_f1 = (2 * overall_precision * overall_recall / (overall_precision + overall_recall)) if (overall_precision + overall_recall) > 0 else 0

    return {
        "per_class": per_class,
        "overall": {
            "precision": round(overall_precision, 4),
            "recall": round(overall_recall, 4),
            "f1": round(overall_f1, 4),
        },
        "columns": len(all_keys),
    }