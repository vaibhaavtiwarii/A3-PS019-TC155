"""
Evidence linking: connects detected PII fields to declared metadata
and checks against the evidence checklist.
"""

import yaml
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from .engine import Finding


# Checklist item kinds
METADATA = "metadata"
DETECTION = "detection"

# Review statuses
STATUS_COMPLETE = "Candidate: checklist complete"
STATUS_GAP = "EVIDENCE GAP FLAG"


@dataclass
class ChecklistItem:
    item: str
    label: str
    kind: str
    required: bool
    present: bool = False


def load_checklist(path: str = "config/checklist.yaml") -> dict:
    """Load and validate the evidence checklist from YAML."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    items: dict[str, dict] = {}
    for key, spec in raw.get("items", {}).items():
        kind = spec.get("kind")
        if kind not in (METADATA, DETECTION):
            raise ValueError(f"Unknown checklist item kind: {kind}")
        if kind == DETECTION and key not in ("name_hint", "value_check"):
            raise ValueError(f"Unknown detection item: {key}")
        items[key] = {
            "item": key,
            "label": spec.get("label", key),
            "kind": kind,
            "required": False,  # Will be set below
            "min_pass_rate": spec.get("min_pass_rate", 0.8),
        }

    required = set(raw.get("required", []))
    advisory = set(raw.get("advisory", []))
    overrides = raw.get("overrides", {})

    # Validate references
    all_known = set(items.keys())
    for r in required:
        if r not in all_known:
            raise ValueError(f"Required item not defined: {r}")
    for a in advisory:
        if a not in all_known:
            raise ValueError(f"Advisory item not defined: {a}")

    for cls, spec in overrides.items():
        for r in spec.get("required", []):
            if r not in all_known:
                raise ValueError(f"Override required item not defined: {r}")
        for a in spec.get("advisory", []):
            if a not in all_known:
                raise ValueError(f"Override advisory item not defined: {a}")

    # Build final checklist with per-class overrides
    final: dict[str, list[dict]] = {}
    for cls in ("NAME", "EMAIL", "PHONE", "GOVT_ID", "DOB", "NONE"):
        cls_required = set(overrides.get(cls, {}).get("required", required))
        cls_advisory = set(overrides.get(cls, {}).get("advisory", advisory))

        cls_items = []
        for key in items:
            item = items[key].copy()
            item["required"] = key in cls_required
            cls_items.append(item)
        final[cls] = cls_items

    return final


def load_metadata(path: str = "config/metadata.yaml") -> dict:
    """Load declared metadata from YAML."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return raw.get("fields", {})


def _make_key(source: str, table: str, column: str) -> str:
    """Create metadata lookup key."""
    return f"{source}:{table}:{column}"


def _check_metadata_item(finding: Finding, meta: dict, item: str) -> bool:
    """Check if a metadata item is present for this finding."""
    key = _make_key(finding.source, finding.table, finding.column)
    return key in meta and item in meta[key] and meta[key][item]


def _check_detection_item(finding: Finding, item: str, min_pass_rate: float) -> bool:
    """Check if a detection item is satisfied."""
    if item == "name_hint":
        return finding.name_score > 0
    if item == "value_check":
        return finding.value_score >= min_pass_rate
    return False


def link(findings: list[Finding], metadata: dict, checklist: dict) -> list[Finding]:
    """
    Link findings to metadata and evaluate checklist.
    Modifies findings in place and returns them.
    """
    for f in findings:
        if f.cls == "NONE":
            continue

        cls_checklist = checklist.get(f.cls, checklist.get("NONE", []))
        gaps = []
        evaluated = []

        for item_spec in cls_checklist:
            item = item_spec["item"]
            kind = item_spec["kind"]
            required = item_spec["required"]

            if kind == METADATA:
                present = _check_metadata_item(f, metadata, item)
            else:  # DETECTION
                min_pass = item_spec.get("min_pass_rate", 0.8)
                present = _check_detection_item(f, item, min_pass)

            evaluated.append(ChecklistItem(
                item=item,
                label=item_spec["label"],
                kind=kind,
                required=required,
                present=present,
            ))

            if required and not present:
                gaps.append(f"MISSING_{item.upper()}")

        # Special case: no metadata entry at all
        key = _make_key(f.source, f.table, f.column)
        if key not in metadata:
            if "NO_METADATA_ENTRY" not in gaps:
                gaps.insert(0, "NO_METADATA_ENTRY")

        f.gaps = gaps
        f.review_status = STATUS_GAP if gaps else STATUS_COMPLETE
        f.checklist = [
            {"item": c.item, "label": c.label, "kind": c.kind,
             "required": c.required, "present": c.present}
            for c in evaluated
        ]

    return [f for f in findings if f.cls != "NONE"]


def orphaned_metadata(findings: list[Finding], metadata: dict) -> list[str]:
    """Find metadata entries that have no corresponding finding."""
    found_keys = {
        _make_key(f.source, f.table, f.column)
        for f in findings
        if f.cls != "NONE"
    }
    return sorted(k for k in metadata if k not in found_keys)