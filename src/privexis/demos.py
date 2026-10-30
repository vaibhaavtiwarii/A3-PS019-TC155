"""
Demo cases for 'Try to fool it' - synthetic columns that test the detector.
"""

from dataclasses import dataclass
from typing import Optional

from .engine import load_config, score_column, Rule, ScoringConfig
from .sampler import ColumnSample


@dataclass
class DemoCase:
    column: str
    values: list[str]
    truth: str
    title: str


def build_cases() -> list[DemoCase]:
    """Build the standard set of demo cases."""
    return [
        DemoCase(
            column="ref_no",
            values=["2345 6789 0124"] * 5,
            truth="GOVT_ID",
            title="Aadhaar in a column called ref_no",
        ),
        DemoCase(
            column="x1",
            values=["asha.sharma@example.com"] * 5,
            truth="EMAIL",
            title="Email in a column called x1",
        ),
        DemoCase(
            column="col_a",
            values=["9876543210"] * 5,
            truth="PHONE",
            title="Phone in a column called col_a",
        ),
        DemoCase(
            column="col_d",
            values=["1990-05-17"] * 5,
            truth="DOB",
            title="Birth date in a column called col_d",
        ),
        DemoCase(
            column="aadhaar",
            values=["2345 6789 0123"] * 5,  # Invalid checksum
            truth="NONE",
            title="Fake Aadhaar (fails checksum) in aadhaar column",
        ),
        DemoCase(
            column="full_name",
            values=["Asha Sharma"] * 5,
            truth="NAME",
            title="Real name in full_name column",
        ),
        DemoCase(
            column="created_at",
            values=["2023-01-15"] * 5,
            truth="NONE",
            title="Creation date (not DOB) in created_at",
        ),
        DemoCase(
            column="emp_code",
            values=["9876543210"] * 5,
            truth="NONE",
            title="Employee code (looks like phone) in emp_code",
        ),
    ]


def name_only_guess(column: str, rules: list[Rule]) -> str:
    """
    Simulate a tool that ONLY looks at column names (no value analysis).
    Returns the first class whose name_hints match, or NONE.
    """
    from .engine import _normalize_column, _check_hint
    normalized = _normalize_column(column)
    for rule in rules:
        if _check_hint(normalized, rule.name_hints):
            return rule.cls
    return "NONE"


def probe(
    column: str,
    values: list[str],
    rules: list[Rule],
    scoring: ScoringConfig,
) -> object:
    """
    Run the detector on a single synthetic column.
    Returns a Finding-like object with .cls attribute.
    """
    sample = ColumnSample(
        source="demo.csv", table="-", column=column,
        values=values[:50], non_empty=len([v for v in values if v.strip()])
    )
    return score_column(sample, rules, scoring)