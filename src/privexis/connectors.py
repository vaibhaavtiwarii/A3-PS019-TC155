"""Connectors: read CSV and SQLite through one common interface.

Both yield Table objects whose rows are a lazy iterator (no giant lists in memory).
Nothing here ever writes to the file it reads."""
import csv
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))   # long free-text cells are fine

CSV_SUFFIXES = {".csv", ".tsv"}
SQLITE_SUFFIXES = {".sqlite", ".sqlite3", ".db"}
SUPPORTED_SUFFIXES = CSV_SUFFIXES | SQLITE_SUFFIXES
_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")     # latin-1 accepts any byte: last resort


@dataclass
class Table:
    source: str            # file name, e.g. "onboarding.csv"
    name: str              # table name; "-" for CSV files
    columns: list          # column names, in order
    rows: Iterator         # iterator of row tuples/lists


def _detect_encoding(path: Path) -> str:
    for enc in _ENCODINGS[:-1]:
        try:
            with open(path, encoding=enc) as f:
                while f.read(1 << 20):
                    pass
            return enc
        except UnicodeDecodeError:
            continue
    return _ENCODINGS[-1]


def _detect_dialect(path: Path, encoding: str):
    with open(path, encoding=encoding, newline="") as f:
        head = f.read(16384)
    if path.suffix.lower() == ".tsv":
        return csv.excel_tab
    try:
        return csv.Sniffer().sniff(head, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def _clean_header(raw: list) -> list:
    """Blank names become col_N; repeated names get a numeric suffix so columns stay distinct."""
    out, seen = [], {}
    for i, h in enumerate(raw):
        h = (h or "").strip() or f"col_{i + 1}"
        n = seen.get(h, 0)
        seen[h] = n + 1
        out.append(h if n == 0 else f"{h}_{n + 1}")
    return out


def _csv_tables(path: Path) -> Iterator[Table]:
    enc = _detect_encoding(path)
    dialect = _detect_dialect(path, enc)

    def rows():
        with open(path, newline="", encoding=enc) as f:
            reader = csv.reader(f, dialect)
            next(reader, None)          # skip the header row
            for row in reader:
                if row:                 # skip blank lines
                    yield row

    with open(path, newline="", encoding=enc) as f:
        header = _clean_header(next(csv.reader(f, dialect), []))
    yield Table(path.name, "-", header, rows())


def _sqlite_tables(path: Path) -> Iterator[Table]:
    # mode=ro opens the database READ-ONLY: a scanner must never modify what it inspects.
    con = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    try:
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        for t in names:
            # Table names can't be passed as ? parameters (only values can),
            # so we quote the identifier ourselves.
            safe = t.replace('"', '""')
            cur = con.execute(f'SELECT * FROM "{safe}"')
            cols = [d[0] for d in cur.description]
            yield Table(path.name, t, cols, iter(cur))
    finally:
        con.close()


def iter_tables(path) -> Iterator[Table]:
    """The one entry point. Picks the connector from the file extension."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext in CSV_SUFFIXES:
        return _csv_tables(path)
    if ext in SQLITE_SUFFIXES:
        return _sqlite_tables(path)
    raise ValueError(f"Unsupported source type: {path.name} (use .csv, .tsv, .sqlite, .sqlite3 or .db)")
