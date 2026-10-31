from pathlib import Path
"""Bounded, deterministic sampling of column values using reservoir sampling (Algorithm R)."""
import hashlib
import random
from dataclasses import dataclass

from privexis.connectors import iter_tables
from privexis.nested import expand_json

NULL_TOKENS = frozenset({"", "na", "n/a", "null", "none", "nan", "nil", "-", "--", "?"})


@dataclass
class ColumnSample:
    source: str
    table: str
    column: str
    values: list              # at most k non-empty values, as stripped strings
    non_empty: int            # how many non-empty values the column had in total
    n_rows: int = 0           # rows seen in the table
    container: bool = False   # a JSON column: its inner fields are separate ColumnSamples

    @property
    def sampled(self) -> bool:
        """True when the sample is a strict subset of the column."""
        return self.non_empty > len(self.values)


def _rng(seed: int, *key: str) -> random.Random:
    """One RNG per column, seeded from the column's identity: the same file always gives the
    same sample, and adding or removing other columns never changes it."""
    digest = hashlib.sha256("|".join((str(seed), *key)).encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def sample_path(path, k: int = 50, seed: int = 42) -> list:
    """Return one ColumnSample per column in every table of the file."""
    results = []
    for table in iter_tables(path):
        n = len(table.columns)
        rngs = [_rng(seed, table.source, table.name, c) for c in table.columns]
        reservoirs = [[] for _ in range(n)]
        seen, rows = [0] * n, 0

        for row in table.rows:               # single pass over the data
            rows += 1
            for i, raw in enumerate(row[:n]):  # [:n] guards against ragged rows
                if raw is None or isinstance(raw, (bytes, bytearray, memoryview)):
                    continue
                v = str(raw).strip()
                if v.lower() in NULL_TOKENS:
                    continue
                seen[i] += 1
                if len(reservoirs[i]) < k:
                    reservoirs[i].append(v)
                else:
                    j = rngs[i].randint(0, seen[i] - 1)
                    if j < k:                # replace with probability k / seen
                        reservoirs[i][j] = v

        table_samples = [ColumnSample(table.source, table.name, col, reservoirs[i], seen[i], rows)
                         for i, col in enumerate(table.columns)]
        results += expand_json(table_samples)
    return results


NOT_DATA = {"labels.csv", "metadata.csv", "gaps.csv"}     # answer keys and metadata files are not sources


def find_sources(root) -> list:
    """CSV, TSV and SQLite files directly under a directory (answer keys excluded)."""
    from privexis.connectors import SUPPORTED_SUFFIXES
    root = Path(root)
    return sorted(p for p in root.iterdir()
                  if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES and p.name.lower() not in NOT_DATA)
