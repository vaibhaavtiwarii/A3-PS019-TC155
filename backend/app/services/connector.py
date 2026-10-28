import sqlite3
import csv
from pathlib import Path
from typing import Iterator, List
from dataclasses import dataclass

@dataclass
class Table:
    source: str
    name: str
    columns: List[str]
    rows: Iterator

class DataConnector:
    """Professional data access layer for PII scanning."""

    def __init__(self, base_path: str = ""):
        self.base_path = Path(base_path)

    def get_tables(self, file_path: str) -> Iterator[Table]:
        full_path = self.base_path / file_path
        ext = full_path.suffix.lower()

        if ext == ".csv":
            yield from self._csv_tables(full_path)
        elif ext in (".sqlite", ".db", ".sqlite3"):
            yield from self._sqlite_tables(full_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def _csv_tables(self, path: Path) -> Iterator[Table]:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, [])

            # We use a generator to keep memory usage low
            def row_generator():
                with open(path, newline="", encoding="utf-8-sig") as f_inner:
                    reader_inner = csv.reader(f_inner)
                    next(reader_inner, None) # skip header
                    yield from reader_inner

            yield Table(path.name, "-", header, row_generator())

    def _sqlite_tables(self, path: Path) -> Iterator[Table]:
        # Open in read-only mode to prevent accidental modification
        conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                # Secure identifier quoting to prevent SQL injection
                safe_name = table_name.replace('"', '""')
                cur = conn.execute(f'SELECT * FROM "{safe_name}"')
                cols = [d[0] for d in cur.description]

                # Use a lambda to ensure connection stays open during iteration
                def row_generator(c=cur):
                    yield from c

                yield Table(path.name, table_name, cols, row_generator())
        finally:
            conn.close()

    def sample_column(self, table: Table, column_index: int, sample_size: int = 50) -> List[str]:
        """Extracts a sample of values from a specific column for analysis."""
        values = []
        try:
            for row in table.rows:
                if len(row) > column_index:
                    values.append(str(row[column_index]))
                if len(values) >= sample_size:
                    break
        except Exception:
            pass
        return values
