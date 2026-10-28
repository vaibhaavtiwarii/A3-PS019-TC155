import re
from typing import List, Optional, Tuple
import yaml
from presidio_analyzer import AnalyzerEngine
from .schemas import PIIFinding, ConfidenceLevel

class HybridPIIEngine:
    def __init__(self, rules_path: str = "config/rules.yaml"):
        self.rules = self._load_config(rules_path)
        self.scoring = self._load_scoring(rules_path)
        self.nlp_analyzer = AnalyzerEngine()

    def _load_config(self, path: str):
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        rules = []
        for cls, spec in raw["classes"].items():
            rules.append({
                "cls": cls,
                "name_hints": [h.lower() for h in spec.get("name_hints", [])],
                "patterns": [re.compile(p) for p in spec.get("value_patterns", [])],
                "negative_hints": [h.lower() for h in spec.get("negative_hints", [])],
                "check": spec.get("check", "pattern and validator")
            })
        return rules

    def _load_scoring(self, path: str):
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        return raw.get("scoring", {"name_weight": 0.3, "value_weight": 0.7, "threshold": 0.5})

    def _normalize(self, col: str) -> str:
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", col)
        return "_".join(t for t in re.split(r"[^A-Za-z0-9]+", s.lower()) if t)

    def _check_name_hint(self, col: str, hints: List[str]) -> Optional[str]:
        padded = f"_{self._normalize(col)}_"
        for h in hints:
            if f"_{h}_" in padded:
                return h
        return None

    def _validate_checksums(self, value: str, pii_class: str) -> bool:
        """
        Implements professional validation (Luhn, etc.)
        to reduce false positives.
        """
        val = str(value).strip().replace(" ", "").replace("-", "")

        if pii_class == "CREDIT_CARD":
            # Luhn Algorithm
            if not val.isdigit(): return False
            digits = [int(d) for d in val]
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9: digits[i] -= 9
            return sum(digits) % 10 == 0

        return True # Default to true for non-checksum types

    def analyze_column(self, source: str, table: str, column: str, values: List[str]) -> PIIFinding:
        best_conf = -1.0
        best_cls = "NONE"
        best_evidence = ""
        best_name_score = 0.0
        best_val_score = 0.0

        # --- Pass 1: Deterministic YAML Rules ---
        for rule in self.rules:
            # Check negative hints (Hard Blockers)
            if self._check_name_hint(column, rule["negative_hints"]):
                continue

            name_hint = self._check_name_hint(column, rule["name_hints"])
            name_score = 1.0 if name_hint else 0.0

            # Value verification
            passed_count = 0
            for v in values:
                if any(p.match(str(v)) for p in rule["patterns"]):
                    if self._validate_checksums(str(v), rule["cls"]):
                        passed_count += 1

            val_score = passed_count / len(values) if values else 0.0
            conf = (self.scoring["name_weight"] * name_score) + (self.scoring["value_weight"] * val_score)

            if conf > best_conf:
                best_conf = conf
                best_cls = rule["cls"]
                best_name_score = name_score
                best_val_score = val_score
                best_evidence = f"Matched {rule['check']} ({passed_count}/{len(values)} values)"

        # --- Pass 2: Probabilistic NLP (Presidio) ---
        # We only trigger NLP if the deterministic score is low or medium
        if best_conf < 0.8:
            # Sample a few values for NLP analysis
            sample_text = " ".join(values[:5])
            nlp_results = self.nlp_analyzer.analyze(text=sample_text, language='en')

            if nlp_results:
                # If NLP finds a strong match, we boost the confidence
                nlp_cls = nlp_results[0].entity_type
                # Map Presidio types to your YAML types if necessary
                # For now, we just record it as evidence
                if best_conf < 0.3:
                    best_conf = 0.4 # Boost to 'Review' level
                    best_cls = nlp_cls
                    best_evidence += f" | NLP detected {nlp_cls}"

        # Final Thresholding
        final_cls = best_cls if best_conf >= self.scoring["threshold"] else "NONE"

        # Map confidence to level
        level = ConfidenceLevel.NONE
        if final_cls != "NONE":
            if best_conf > 0.8: level = ConfidenceLevel.HIGH
            elif best_conf > 0.5: level = ConfidenceLevel.MEDIUM
            else: level = ConfidenceLevel.LOW

        return PIIFinding(
            source=source,
            table=table,
            column=column,
            pii_class=final_cls,
            confidence=round(best_conf, 2),
            confidence_level=level,
            evidence=best_evidence,
            name_score=best_name_score,
            value_score=round(best_val_score, 2),
            matched_value_sample=values[0] if values else None
        )
