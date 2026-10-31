"""Guards on the evaluation itself: labelled files must exist, and accuracy must not silently drop."""
from pathlib import Path

from privexis.engine import load_config
from privexis.evaluator import evaluate, load_labels
from privexis.linker import load_checklist
from privexis.pipeline import run_pipeline
from privexis.sampler import find_sources

RULES, SCORING = load_config("config/rules.yaml")
CHECKLIST = load_checklist("config/checklist.yaml")


def _scan(folder):
    truth = {k: v.split("|")[0] for k, v in load_labels(f"{folder}/labels.csv").items()}
    res = run_pipeline(find_sources(folder), RULES, SCORING, {}, CHECKLIST)
    return truth, res, evaluate(res.findings, truth)


def test_every_labelled_file_exists():
    for folder in ("data", "data/holdout", "data/stress/sealed"):
        files = {p.name for p in Path(folder).iterdir()}
        missing = {k[0] for k in load_labels(f"{folder}/labels.csv")} - files
        assert not missing, f"labels refer to files that are not in {folder}: {missing}"


def test_main_and_holdout_sets_are_scored_without_misses():
    for folder in ("data", "data/holdout"):
        _, _, ev = _scan(folder)
        assert ev["overall"]["precision"] == 1.0 and ev["overall"]["recall"] == 1.0, folder


def test_unseen_generated_set_stays_above_a_floor():
    _, _, ev = _scan("data/stress/sealed")
    assert ev["overall"]["f1"] >= 0.80
    assert ev["overall"]["precision"] >= 0.85


def test_missing_metadata_is_flagged_for_the_undeclared_file():
    from privexis.linker import load_metadata
    res = run_pipeline(find_sources("data"), RULES, SCORING, load_metadata("config/metadata.yaml"), CHECKLIST)
    gaps = {f.column: f.gaps for f in res.findings if f.source == "temp_dump.csv"}
    assert gaps and all("NO_METADATA_ENTRY" in g for g in gaps.values())
