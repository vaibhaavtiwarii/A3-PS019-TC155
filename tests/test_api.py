import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.main import scan_demo, get_accuracy, get_rules, get_demos, health


def test_api_health():
    res = health()
    assert res["status"] == "healthy"


def test_api_scan_demo():
    res = scan_demo()
    assert "summary" in res
    assert res["summary"]["total_columns"] > 0
    assert res["summary"]["pii_detected"] > 0
    assert len(res["findings"]) == res["summary"]["pii_detected"]


def test_api_accuracy():
    res = get_accuracy()
    assert "main" in res
    assert "holdout" in res
    assert "precision" in res["main"]["overall"]
    assert "recall" in res["main"]["overall"]


def test_api_rules():
    res = get_rules()
    assert "rules" in res
    assert "classes" in res["rules"]
    assert set(res["rules"]["classes"].keys()) == {"NAME", "EMAIL", "PHONE", "GOVT_ID", "DOB"}


def test_api_demos():
    res = get_demos()
    assert "cases" in res
    assert len(res["cases"]) > 0
    assert all("correct" in c for c in res["cases"])
