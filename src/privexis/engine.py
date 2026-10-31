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

"""Rule engine: fuse column-name hints + value patterns + validators into one score.

    confidence = name_weight * (name hint matched?) + value_weight * (share of sampled values that pass)

Per-class settings in config/rules.yaml control how much a class may rely on its values alone
(see `value_only`) and whether mixed or free-text columns count (`mixed_min`, `embedded_patterns`).
"""
import re
from dataclasses import dataclass, field

import yaml

from privexis import validators as V
from privexis.masking import mask_value


class ConfigError(ValueError):
    """The rules file is invalid; the message says which key and why."""


# Config refers to validators by name; this maps the names to real functions.
# Each takes (value, strong) where `strong` says a very specific column-name hint matched.
def make_validator(name: str, scoring: dict):
    strict_pan = bool(scoring.get("strict_pan", False))
    table = {
        "email": lambda v, strong=False: V.is_email(v),
        "phone": lambda v, strong=False: V.is_phone(v),
        "govt_id": lambda v, strong=False: V.is_govt_id(v, strict_pan),
        "date_plausible": lambda v, strong=False: V.is_plausible_dob(v),
        "person_name": V.is_person_name,
    }
    if name not in table:
        raise ConfigError(f"unknown validator '{name}'. Known: {', '.join(sorted(table))}")
    return table[name]


VALUE_ONLY_MODES = ("flag", "review", "ignore", "distribution")
RULE_KEYS = {"name_hints", "strong_hints", "negative_hints", "value_patterns", "context_patterns",
             "embedded_patterns", "validator", "check", "value_only", "mixed_min", "embedded_min"}


@dataclass
class Rule:
    cls: str
    name_hints: list
    patterns: list                      # compiled regexes: value shape
    validator: object                   # function(value, strong) or None
    negative_hints: list = field(default_factory=list)   # column-name words that rule this class out
    check: str = "pattern and validator"                  # plain-English name of the checks
    strong_hints: list = field(default_factory=list)      # very specific hints (first_name, surname)
    context_patterns: list = field(default_factory=list)  # shapes accepted only WITH a name hint
    embedded_patterns: list = field(default_factory=list)  # look for the value inside free text
    value_only: str = "flag"            # what values alone may do: flag | review | ignore | distribution
    mixed_min: float = 0.0              # flag a column when this share of values passes (0 = off)
    embedded_min: float = 0.0           # flag a free-text column when this share of cells CONTAIN a valid item


@dataclass
class Finding:
    source: str
    table: str
    column: str
    cls: str            # best class, or "NONE" if below threshold
    confidence: float
    name_score: float
    value_score: float
    evidence: str
    classes: list = field(default_factory=list)   # every class at or above the threshold, best first
    closest: str = ""   # best-scoring class even when it fell below the threshold
    kind: str = "full"  # full | mixed | embedded | container
    hint: str = ""      # the column-name hint that matched (if any)
    masked: list = field(default_factory=list)    # up to 3 masked example values
    subtypes: dict = field(default_factory=dict)  # e.g. {"aadhaar": 40, "pan": 3}
    gaps: list = field(default_factory=list)          # filled in by the linker
    review_status: str = ""                           # filled in by the linker
    checklist: list = field(default_factory=list)     # filled in by the linker


class ScoringConfig(dict):
    """The `scoring:` block of rules.yaml. Read it as scoring['threshold'] or scoring.threshold."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


# ----------------------------------------------------------------------------- config
def _patterns(raw, cls, key):
    try:
        return [re.compile(p) for p in raw.get(key, [])]
    except re.error as e:
        raise ConfigError(f"classes.{cls}.{key}: invalid regular expression ({e})") from e


def load_config(path="config/rules.yaml"):
    """Read and validate the rules. Returns (rules, scoring)."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)          # safe_load: never executes code from the file
    if not isinstance(raw, dict) or "classes" not in raw or "scoring" not in raw:
        raise ConfigError("rules file needs top-level 'scoring' and 'classes' sections")
    scoring = ScoringConfig(raw["scoring"])
    try:
        nw, vw, th = (float(scoring[k]) for k in ("name_weight", "value_weight", "threshold"))
    except KeyError as e:
        raise ConfigError(f"scoring.{e.args[0]} is missing") from e
    if min(nw, vw) < 0 or abs(nw + vw - 1.0) > 0.01:
        raise ConfigError("scoring.name_weight + scoring.value_weight must equal 1.0")
    if not 0 < th <= 1:
        raise ConfigError("scoring.threshold must be between 0 and 1")

    rules = []
    for cls, spec in raw["classes"].items():
        spec = spec or {}
        unknown = set(spec) - RULE_KEYS
        if unknown:
            raise ConfigError(f"classes.{cls}: unknown keys {sorted(unknown)}")
        mode = spec.get("value_only", "flag")
        if mode not in VALUE_ONLY_MODES:
            raise ConfigError(f"classes.{cls}.value_only must be one of {VALUE_ONLY_MODES}")
        validator = make_validator(spec["validator"], scoring) if spec.get("validator") else None
        if mode == "distribution" and spec.get("validator") != "date_plausible":
            raise ConfigError(f"classes.{cls}: value_only 'distribution' needs validator date_plausible")
        rules.append(Rule(
            cls=cls,
            name_hints=[normalize(h) for h in spec.get("name_hints", [])],
            patterns=_patterns(spec, cls, "value_patterns"),
            validator=validator,
            negative_hints=[normalize(h) for h in spec.get("negative_hints", [])],
            check=spec.get("check", "pattern and validator"),
            strong_hints=[normalize(h) for h in spec.get("strong_hints", [])],
            context_patterns=_patterns(spec, cls, "context_patterns"),
            embedded_patterns=_patterns(spec, cls, "embedded_patterns"),
            value_only=mode,
            mixed_min=float(spec.get("mixed_min", 0.0)),
            embedded_min=float(spec.get("embedded_min", 0.0)),
        ))
    return rules, scoring


# ----------------------------------------------------------------------- name hints
def normalize(col: str) -> str:
    """'ContactEmail' / 'contact-email' / 'Contact Email' -> 'contact_email'."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(col))     # split camelCase
    return "_".join(t for t in re.split(r"[^A-Za-z0-9]+", s.lower()) if t)


def matched_hint(col: str, hints: list, compact: bool = False):
    """Return the first hint found in the column name, else None.

    Hints match whole words only: 'pan' matches 'pan_no' but NOT 'company'.
    With compact=True a longer hint (5+ letters) may also match inside a joined word, so
    'email' finds 'emailaddr' and 'fullname' finds 'FullName'. Used for positive hints only,
    because 'order' would otherwise rule out 'recorder'."""
    toks = normalize(col).split("_")
    for h in hints:
        ht = h.split("_")
        n = len(ht)
        if any(toks[i:i + n] == ht for i in range(len(toks) - n + 1)):
            return h
    if compact:
        joined = "".join(toks)
        for h in hints:
            flat = h.replace("_", "")
            if len(flat) >= 5 and flat in joined:
                return h
    return None


# ----------------------------------------------------------------------------- scoring
def _value_hits(rule: Rule, values: list, hint, strong: bool):
    """Count sampled values that pass shape + validator (or a context shape when a hint matched)."""
    passed, passing = 0, []
    for v in values:
        ok = (not rule.patterns or any(p.match(v) for p in rule.patterns)) and \
             (rule.validator is None or rule.validator(v, strong))
        if not ok and hint and rule.context_patterns:
            ok = any(p.match(v) for p in rule.context_patterns)
        if ok:
            passed += 1
            passing.append(v)
    return passed, passing


def _embedded_hits(rule: Rule, values: list, strong: bool):
    """Count values that CONTAIN a valid item somewhere inside longer text."""
    hits, found = 0, []
    for v in values:
        for p in rule.embedded_patterns:
            m = next((m.group(0) for m in p.finditer(v)
                      if rule.validator is None or rule.validator(m.group(0), strong)), None)
            if m:
                hits += 1
                found.append(m)
                break
    return hits, found


def _subtypes(rule: Rule, passing: list) -> dict:
    if rule.cls != "GOVT_ID":
        return {}
    out = {}
    for v in passing:
        kind = V.govt_id_kind(v) or "other"
        out[kind] = out.get(kind, 0) + 1
    return out


def _score_rule(rule: Rule, sample, scoring: dict):
    values = sample.values
    hint = matched_hint(sample.column, rule.name_hints, compact=True)
    strong = bool(matched_hint(sample.column, rule.strong_hints, compact=True))
    name_score = 1.0 if hint else 0.0
    threshold = float(scoring["threshold"])

    passed, passing = _value_hits(rule, values, hint, strong)
    n = len(values)
    value_score, kind, examples = (passed / n if n else 0.0), "full", passing
    notes = []

    avg_len = sum(len(v) for v in values) / n if n else 0
    if rule.embedded_patterns and avg_len >= float(scoring.get("embed_min_len", 30)):
        e_hits, e_found = _embedded_hits(rule, values, strong)
        if e_hits / n > value_score:
            value_score, kind, examples, passed = e_hits / n, "embedded", e_found, e_hits
            notes.append(f"found inside free text in {e_hits}/{n} values")

    conf = scoring["name_weight"] * name_score + scoring["value_weight"] * value_score

    if kind == "full" and rule.mixed_min and value_score >= rule.mixed_min and conf < threshold:
        conf, kind = threshold, "mixed"                # a mixed column still stores personal data
        notes.append(f"mixed column: {value_score:.0%} of values pass, the rest do not")
    elif kind == "embedded" and rule.embedded_min and value_score >= rule.embedded_min and conf < threshold:
        conf = threshold                               # personal data typed into free text

    if not hint and rule.value_only == "distribution" and conf > 0:
        if V.birth_like_spread(values):
            notes.append("no column-name hint, but the dates span decades at adult ages like birth dates")
        else:
            notes.append("no column-name hint, and the dates do not look like birth dates "
                         "(not spread over decades at adult ages)")
            conf = 0.0
    elif not hint and rule.value_only != "flag" and conf > 0:
        if rule.value_only == "ignore":
            notes.append("no column-name hint, and this class is not judged by values alone")
            conf = 0.0
        else:
            conf = min(conf, threshold - 0.01)         # shown to a reviewer, never auto-flagged
            notes.append("no column-name hint: values alone only reach 'needs review'")

    parts = []
    if hint:
        parts.append(f"name hint '{hint}'" + (" (strong)" if strong else ""))
    parts.append(f"{passed}/{n} sampled values passed {rule.check}")
    parts += notes
    return {"conf": conf, "cls": rule.cls, "name": name_score, "value": value_score,
            "evidence": "; ".join(parts), "kind": kind, "hint": hint or "",
            "examples": examples, "subtypes": _subtypes(rule, examples) if kind != "embedded" else {}}


def score_column(sample, rules, scoring) -> Finding:
    base = (sample.source, sample.table, sample.column)
    if getattr(sample, "container", False):
        return Finding(*base, "NONE", 0.0, 0.0, 0.0,
                       "JSON container: its inner fields are scanned as separate columns",
                       kind="container")

    threshold = float(scoring["threshold"])
    cands, excluded = [], []
    for rule in rules:
        blocker = matched_hint(sample.column, rule.negative_hints)
        if blocker:                      # e.g. 'created_at' can never be a date of birth
            excluded.append(f"{rule.cls} excluded by negative hint '{blocker}'")
            continue
        cands.append(_score_rule(rule, sample, scoring))

    if not cands:                        # every class was excluded by a negative hint
        return Finding(*base, "NONE", 0.0, 0.0, 0.0,
                       "; ".join(excluded) or "no supporting evidence for any class")

    cands.sort(key=lambda c: -c["conf"])
    best = cands[0]
    flagged = [c for c in cands if c["conf"] >= threshold]
    evidence = best["evidence"]
    if not flagged:
        evidence = ("no supporting evidence for any class" if best["conf"] == 0 else
                    f"below threshold; closest class {best['cls']}: {evidence}")
        if excluded:
            evidence = "; ".join([evidence] + excluded) if best["conf"] else "; ".join(excluded)
    elif len(flagged) > 1:
        evidence += "; also matches " + ", ".join(c["cls"] for c in flagged[1:])

    top = flagged[0] if flagged else best
    cls = top["cls"] if flagged else "NONE"
    return Finding(
        *base, cls, round(best["conf"], 2), best["name"], round(best["value"], 2), evidence,
        classes=[c["cls"] for c in flagged], closest=best["cls"] if best["conf"] > 0 else "",
        kind=top["kind"], hint=top["hint"],
        masked=[mask_value(v, top["cls"]) for v in top["examples"][:3]] if flagged else [],
        subtypes=top["subtypes"] if flagged else {},
    )

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