"""
Core detection engine: scores columns against PII classes using configurable rules.
Combines column-name hints, value patterns, and strict validators.
"""

import re
import yaml
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from .validators import VALIDATORS
from .sampler import ColumnSample


@dataclass
class Rule:
    """A single PII class detection rule."""
    cls: str
    name_hints: list[str]
    negative_hints: list[str]
    patterns: list[re.Pattern]
    validator_name: Optional[str]
    check_description: str


@dataclass
class ScoringConfig:
    name_weight: float
    value_weight: float
    threshold: float
    review_floor: float


@dataclass
class Finding:
    """Result of scoring a single column."""
    source: str
    table: str
    column: str
    cls: str
    confidence: float
    evidence: str
    name_score: float
    value_score: float
    gaps: list[str]
    review_status: str
    checklist: list[dict]


def _normalize_column(name: str) -> str:
    """Normalize column name for hint matching: snake_case, lowercase, words split."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return "_".join(t for t in re.split(r"[^A-Za-z0-9]+", s.lower()) if t)


def _check_hint(normalized: str, hints: list[str]) -> Optional[str]:
    """Check if any hint matches as a whole word in the normalized column name."""
    padded = f"_{normalized}_"
    for h in hints:
        if f"_{h}_" in padded:
            return h
    return None


def load_config(path: str = "config/rules.yaml") -> tuple[list[Rule], ScoringConfig]:
    """
    Load detection rules and scoring config from YAML.
    Returns (rules_list, scoring_config).
    """
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    scoring = ScoringConfig(**raw.get("scoring", {
        "name_weight": 0.4,
        "value_weight": 0.6,
        "threshold": 0.5,
        "review_floor": 0.1,
    }))

    rules: list[Rule] = []
    for cls, spec in raw.get("classes", {}).items():
        rules.append(Rule(
            cls=cls,
            name_hints=[h.lower() for h in spec.get("name_hints", [])],
            negative_hints=[h.lower() for h in spec.get("negative_hints", [])],
            patterns=[re.compile(p) for p in spec.get("value_patterns", [])],
            validator_name=spec.get("validator"),
            check_description=spec.get("check", "pattern match"),
        ))

    return rules, scoring


def score_column(sample: ColumnSample, rules: list[Rule], scoring: ScoringConfig) -> Finding:
    """
    Score a single column against all rules.
    Returns the best-matching class finding.
    """
    normalized = _normalize_column(sample.column)
    best_conf = -1.0
    best_cls = "NONE"
    best_evidence = ""
    best_name_score = 0.0
    best_val_score = 0.0
    blocked_by = []

    for rule in rules:
        # Negative hints are hard blockers
        neg_hit = _check_hint(normalized, rule.negative_hints)
        if neg_hit:
            blocked_by.append(f"negative hint '{neg_hit}'")
            continue

        # Name hint score (0 or 1)
        name_hit = _check_hint(normalized, rule.name_hints)
        name_score = 1.0 if name_hit else 0.0

        # Value pattern + validator score
        passed = 0
        for val in sample.values:
            if any(p.match(val) for p in rule.patterns):
                # Strict validator check
                validator = VALIDATORS.get(rule.validator_name) if rule.validator_name else None
                if validator is None or validator(val):
                    passed += 1

        val_score = passed / len(sample.values) if sample.values else 0.0

        # Combined confidence
        conf = (scoring.name_weight * name_score) + (scoring.value_weight * val_score)

        if conf > best_conf:
            best_conf = conf
            best_cls = rule.cls
            best_name_score = name_score
            best_val_score = val_score
            hint_part = f" + name hint '{name_hit}'" if name_hit else ""
            best_evidence = f"Matched {rule.check_description} ({passed}/{len(sample.values)} values){hint_part}"

    # Final thresholding
    final_cls = best_cls if best_conf >= scoring.threshold else "NONE"
    if final_cls == "NONE" and blocked_by:
        best_evidence = f"Blocked by {blocked_by[0]}"

    return Finding(
        source=sample.source,
        table=sample.table,
        column=sample.column,
        cls=final_cls,
        confidence=round(best_conf, 3),
        evidence=best_evidence,
        name_score=best_name_score,
        value_score=round(best_val_score, 3),
        gaps=[],  # Filled in by linker
        review_status="",
        checklist=[],
    )