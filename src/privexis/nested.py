"""Expand JSON-object columns into one virtual column per key ('profile.email').

Personal data often hides inside a JSON text cell. The parent column is marked as a container
and each inner field is scored like any other column."""
import json
from dataclasses import replace

MAX_DEPTH = 2


def _flatten(obj: dict, prefix: str, depth: int, out: dict) -> None:
    for key, val in obj.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(val, dict) and depth < MAX_DEPTH:
            _flatten(val, path, depth + 1, out)
        elif isinstance(val, (str, int, float)) and not isinstance(val, bool):
            text = str(val).strip()
            if text:
                out.setdefault(path, []).append(text)


def expand_json(samples: list, min_share: float = 0.7) -> list:
    """Replace each JSON-object column by a container marker plus one sample per inner key."""
    result = []
    for s in samples:
        values = s.values
        likely = [v for v in values if v.startswith("{") and v.endswith("}")]
        if not values or len(likely) / len(values) < min_share:
            result.append(s)
            continue
        fields, parsed = {}, 0
        for v in likely:
            try:
                obj = json.loads(v)
            except ValueError:
                continue
            if isinstance(obj, dict):
                parsed += 1
                _flatten(obj, "", 1, fields)
        if parsed / len(values) < min_share:
            result.append(s)
            continue
        result.append(replace(s, values=[], container=True))
        for path in sorted(fields):
            vals = fields[path]
            result.append(replace(s, column=f"{s.column}.{path}", values=vals,
                                  non_empty=len(vals), container=False))
    return result
