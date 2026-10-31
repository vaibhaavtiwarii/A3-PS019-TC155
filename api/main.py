"""
Privexis API — FastAPI backend wrapping the core privexis library.
Provides endpoints for scanning, evidence, gaps, accuracy, rules, and demos.
"""
import os

import sys
import time
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure src/ is on path for privexis imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from privexis.pipeline import run_pipeline, PipelineResult, parse_metadata
from privexis.engine import load_config
from privexis.linker import load_checklist, load_metadata
from privexis.evaluator import load_labels, evaluate
from privexis.sampler import find_sources
from privexis.demos import build_cases, probe, name_only_guess

# Project paths
ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"

app = FastAPI(title="Privexis API", version="2.0.0")

# Browser origins allowed to call this API. The deployed frontend must be listed, or the
# browser blocks every request. Extra origins: set CORS_ORIGINS="https://a.com,https://b.com".
_ALLOWED_ORIGINS = [
    "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
    "https://a3-ps-019-tc-155.vercel.app",
] + [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]

# Browser origins allowed to call this API. The deployed frontend must be listed, or the
# browser blocks every request. Extra origins: set CORS_ORIGINS="https://a.com,https://b.com".
_ALLOWED_ORIGINS = [
    "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
    "https://a3-ps-019-tc-155.vercel.app",
] + [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask(val: str) -> str:
    """Mask a sample value for safe display."""
    if not val or len(val) <= 3:
        return "***"
    return val[:2] + "*" * min(len(val) - 2, 8)


def _build_response(
    result: PipelineResult,
    metadata: dict,
    paths: list,
    elapsed: float,
    findings: list = None,
) -> dict:
    """Convert a PipelineResult to the JSON response format."""
    # Gap tally
    gap_tally: dict[str, int] = {}
    if findings:
        for f in findings:
            for g in f.gaps:
                gap_tally[g] = gap_tally.get(g, 0) + 1
    else:
        for f in result.findings:
            for g in f.gaps:
                gap_tally[g] = gap_tally.get(g, 0) + 1
        for g in f.gaps:
            gap_tally[g] = gap_tally.get(g, 0) + 1

    # Tier mapping
    def _tier_for_class(cls: str) -> str:
        if cls == "GOVT_ID":
            return "Critical tier"
        elif cls in ("NAME", "DOB"):
            return "High tier"
        return "Medium tier"

    # Findings (PII detected)
    findings_out = []
    for f in result.findings:
        key = f"{f.source}:{f.table}:{f.column}"
        meta = metadata.get(key, {})
        raw = result.samples.get((f.source, f.table, f.column), [])
        findings_out.append({
            "source": f.source,
            "table": f.table,
            "column": f.column,
            "cls": f.cls,
            "tier": _tier_for_class(f.cls),
            "confidence": f.confidence,
            "evidence": f.evidence,
            "name_score": f.name_score,
            "value_score": f.value_score,
            "gaps": f.gaps,
            "review_status": f.review_status,
            "checklist": f.checklist,
            "purpose": meta.get("purpose"),
            "retention": meta.get("retention"),
            "owner": meta.get("owner"),
            "sample_values": [_mask(v) for v in raw[:5]],
            "suggested_next_step": (
                f"No evidence gaps found for {f.source}:{f.column} in the supplied metadata."
                if not f.gaps else f"Evidence gaps detected for {f.source}:{f.column}: {', '.join(f.gaps)}. Review metadata for purpose, retention, and owner."
            ),
        })

    # Needs-review columns
    review_out = [
        {
            "source": f.source,
            "table": f.table,
            "column": f.column,
            "confidence": f.confidence,
            "evidence": f.evidence,
        }
        for f in result.review
    ]

    # Metrics computation
    total_pii = len(result.findings)
    class_breakdown: dict[str, int] = {}
    for f in result.findings:
        class_breakdown[f.cls] = class_breakdown.get(f.cls, 0) + 1

    metadata_linked = sum(1 for f in findings_out if f.get("purpose") and f.get("retention"))
    coverage_pct = round((metadata_linked / total_pii * 100), 1) if total_pii > 0 else 0

    critical_gaps = sum(1 for f in result.findings if f.cls == "GOVT_ID" and f.gaps)
    high_gaps = sum(1 for f in result.findings if any("PURPOSE" in g or "RETENTION" in g for g in f.gaps) and f.cls != "GOVT_ID")
    medium_gaps = sum(1 for f in result.findings if any("OWNER" in g or "VALUE" in g for g in f.gaps) and not any("PURPOSE" in g or "RETENTION" in g for g in f.gaps))

    return {
        "summary": {
            "total_columns": len(result.all_columns),
            "pii_detected": len(result.findings),
            "gap_count": sum(1 for f in result.findings if f.gaps),
            "metadata_linked": metadata_linked,
            "evidence_coverage": coverage_pct,
            "execution_time": elapsed,
            "files_scanned": len(paths),
            "class_breakdown": class_breakdown,
            "severity": {
                "critical": critical_gaps,
                "high": high_gaps,
                "medium": medium_gaps,
            },
        },
        "findings": findings_out,
        "review": review_out,
        "orphaned_metadata": result.orphaned,
        "gap_tally": gap_tally,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "online", "message": "Privexis API is running"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/scan")
async def scan_files(
    files: list[UploadFile] = File(...),
    metadata_file: Optional[UploadFile] = File(default=None),
):
    """Scan uploaded CSV / SQLite files for PII."""
    # Secure upload directory - isolated per request
    upload_dir = Path(tempfile.mkdtemp(prefix="privexis_upload_"))
    try:
        paths: list[Path] = []
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

        for f in files:
            # Validate file size
            if f.size and f.size > MAX_FILE_SIZE:
                raise HTTPException(413, f"File size exceeds limit of 10MB: {f.filename}")

            # Sanitize filename to prevent path traversal
            # Use only the basename, no directory components
            original_name = Path(f.filename).name
            safe_name = Path(original_name).name  # strips any path components
            if not safe_name or safe_name.startswith('.') or '..' in safe_name or Path(f.filename).is_absolute():
                raise HTTPException(400, f"Invalid filename: {f.filename}")

            ext = Path(safe_name).suffix.lower()
            if ext not in (".csv", ".sqlite", ".db", ".sqlite3"):
                raise HTTPException(400, f"Unsupported file type: {ext}")

            dest = upload_dir / safe_name
            content = await f.read()

            # Double-check actual size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(413, f"File size exceeds limit of 10MB: {safe_name}")

            dest.write_bytes(content)
            paths.append(dest)

        extra: dict = {}
        if metadata_file:
            extra = parse_metadata(await metadata_file.read(), metadata_file.filename)

        rules, scoring = load_config(str(CONFIG_DIR / "rules.yaml"))
        checklist = load_checklist(str(CONFIG_DIR / "checklist.yaml"))
        base_meta = load_metadata(str(CONFIG_DIR / "metadata.yaml"))
        metadata = {**base_meta, **extra}

        start = time.time()
        result = run_pipeline(paths, rules, scoring, metadata, checklist)
        elapsed = round(time.time() - start, 3)

        return _build_response(result, metadata, paths, elapsed)
    finally:
        shutil.rmtree(upload_dir, ignore_errors=True)


@app.post("/api/scan-demo")
def scan_demo():
    """Scan the built-in demo data files."""
    sources = [s for s in find_sources(DATA_DIR) if s.name != "labels.csv"]
    if not sources:
        raise HTTPException(404, "No demo data files found")

    rules, scoring = load_config(str(CONFIG_DIR / "rules.yaml"))
    checklist = load_checklist(str(CONFIG_DIR / "checklist.yaml"))
    metadata = load_metadata(str(CONFIG_DIR / "metadata.yaml"))

    start = time.time()
    result = run_pipeline(sources, rules, scoring, metadata, checklist)
    elapsed = round(time.time() - start, 3)

    return _build_response(result, metadata, sources, elapsed)


@app.get("/api/accuracy")
def get_accuracy():
    """Per-class precision / recall / F1 on both labelled sets."""
    rules, scoring = load_config(str(CONFIG_DIR / "rules.yaml"))
    checklist = load_checklist(str(CONFIG_DIR / "checklist.yaml"))
    metadata = load_metadata(str(CONFIG_DIR / "metadata.yaml"))
    out: dict = {}

    # Main labelled set
    main_labels = DATA_DIR / "labels.csv"
    if main_labels.exists():
        sources = [s for s in find_sources(DATA_DIR) if s.name != "labels.csv"]
        result = run_pipeline(sources, rules, scoring, metadata, checklist)
        truth = load_labels(main_labels)
        out["main"] = evaluate(result.findings, truth)

    # Holdout set
    holdout_dir = DATA_DIR / "holdout"
    holdout_labels = holdout_dir / "labels.csv"
    if holdout_labels.exists():
        h_sources = [s for s in find_sources(holdout_dir) if s.name != "labels.csv"]
        h_result = run_pipeline(h_sources, rules, scoring, {}, checklist)
        h_truth = load_labels(holdout_labels)
        out["holdout"] = evaluate(h_result.findings, h_truth)

    # Unseen generated set (names and vocabulary the rules were not written against)
    unseen_dir = DATA_DIR / "stress" / "sealed"
    unseen_labels = unseen_dir / "labels.csv"
    if unseen_labels.exists():
        u_result = run_pipeline(find_sources(unseen_dir), rules, scoring, {}, checklist)
        u_truth = {k: v.split("|")[0] for k, v in load_labels(unseen_labels).items()}
        out["unseen"] = evaluate(u_result.findings, u_truth)

    return out


@app.get("/api/rules")
def get_rules():
    """Return current detection rules and checklist configuration."""
    with open(CONFIG_DIR / "rules.yaml", encoding="utf-8") as f:
        rules_raw = yaml.safe_load(f)
    with open(CONFIG_DIR / "checklist.yaml", encoding="utf-8") as f:
        checklist_raw = yaml.safe_load(f)
    return {"rules": rules_raw, "checklist": checklist_raw}


@app.get("/api/demos")
def get_demos():
    """Run 'try to fool it' demo cases and return results."""
    rules, scoring = load_config(str(CONFIG_DIR / "rules.yaml"))
    cases = build_cases()
    results = []
    for case in cases:
        finding = probe(case.column, case.values, rules, scoring)
        ng = name_only_guess(case.column, rules)
        results.append({
            "title": case.title,
            "column": case.column,
            "values": [_mask(v) for v in case.values[:3]],
            "truth": case.truth,
            "predicted": finding.cls,
            "confidence": finding.confidence,
            "evidence": finding.evidence,
            "name_only_guess": ng,
            "correct": finding.cls == case.truth,
        })
    return {"cases": results}


class MetadataUpdateRequest(BaseModel):
    source: str
    table: str = "-"
    column: str
    purpose: Optional[str] = None
    retention: Optional[str] = None
    owner: Optional[str] = None


@app.post("/api/metadata/update")
def update_metadata(req: MetadataUpdateRequest):
    """Update declared purpose/retention for a field to resolve an evidence gap."""
    key = f"{req.source}:{req.table}:{req.column}"
    meta_path = CONFIG_DIR / "metadata.yaml"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = yaml.safe_load(f) or {}

    if "fields" not in meta_data:
        meta_data["fields"] = {}

    entry = meta_data["fields"].get(key, {})
    if req.purpose:
        entry["purpose"] = req.purpose
    if req.retention:
        entry["retention"] = req.retention
    if req.owner:
        entry["owner"] = req.owner

    meta_data["fields"][key] = entry
    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(meta_data, f, sort_keys=False)

    return scan_demo()



