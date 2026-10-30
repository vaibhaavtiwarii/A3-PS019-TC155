"""
Reservoir sampling for deterministic, bounded column samples.
Ensures reproducibility with a fixed seed.
"""

import csv
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional
import random


@dataclass
class ColumnSample:
    """A sampled column with its values and metadata."""
    source: str
    table: str
    column: str
    values: List[str]
    non_empty: int


def _reservoir_sample(rows: Iterator[List[str]], col_idx: int, k: int) -> tuple[List[str], int]:
    """
    Reservoir sampling (Algorithm R) - one pass, O(k) memory.
    Returns (sample_values, non_empty_count).
    """
    random.seed(42)  # Fixed seed for reproducibility
    reservoir: List[str] = []
    non_empty = 0

    for i, row in enumerate(rows):
        if col_idx < len(row):
            val = str(row[col_idx]).strip()
            if val:
                non_empty += 1
                if len(reservoir) < k:
                    reservoir.append(val)
                else:
                    j = random.randint(0, i)
                    if j < k:
                        reservoir[j] = val
    return reservoir, non_empty


def _csv_rows(path: Path) -> Iterator[List[str]]:
    """Yield rows from a CSV file."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        yield from reader


def _sqlite_rows(path: Path, table: str) -> Iterator[List[str]]:
    """Yield rows from a SQLite table (read-only)."""
    conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    try:
        safe_name = table.replace('"', '""')
        cursor = conn.execute(f'SELECT * FROM "{safe_name}"')
        yield from cursor
    finally:
        conn.close()


def sample_path(path: str | Path, k: int = 50) -> List[ColumnSample]:
    """
    Sample up to k values from each column of a CSV or SQLite file.

    Args:
        path: Path to CSV or SQLite file
        k: Maximum sample size per column

    Returns:
        List of ColumnSample objects, one per column
    """
    path = Path(path)
    ext = path.suffix.lower()
    results: List[ColumnSample] = []

    if ext == ".csv":
        # Read header first
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, [])

        for i, col_name in enumerate(header):
            rows = _csv_rows(path)
            values, non_empty = _reservoir_sample(rows, i, k)
            results.append(ColumnSample(
                source=path.name, table="-", column=col_name,
                values=values, non_empty=non_empty
            ))

    elif ext in (".sqlite", ".db", ".sqlite3"):
        conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                safe_name = table.replace('"', '""')
                cur = conn.execute(f'SELECT * FROM "{safe_name}"')
                cols = [d[0] for d in cur.description]

                for i, col_name in enumerate(cols):
                    rows = _sqlite_rows(path, table)
                    values, non_empty = _reservoir_sample(rows, i, k)
                    results.append(ColumnSample(
                        source=path.name, table=table, column=col_name,
                        values=values, non_empty=non_empty
                    ))
        finally:
            conn.close()
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    return results


def find_sources(root: str | Path) -> List[Path]:
    """Find all CSV and SQLite files under a directory."""
    root = Path(root)
    files = list(root.glob("*.csv")) + list(root.glob("*.sqlite"))
    return sorted(files)