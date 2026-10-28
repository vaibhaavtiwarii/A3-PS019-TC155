# Privexis Elite: Technical Architecture & Discovery Pipeline

This document outlines the high-level logic of the Privexis Elite system, a hybrid personal-data discovery engine.

## 1. High-Level System Flow
The system is split into a decoupled **FastAPI Backend** and a **React Enterprise Frontend**.

```text
Frontend (React) -> API Request (/scan) -> Backend (FastAPI) -> Discovery Engine -> Data Connector -> Result JSON -> Frontend UI
```

## 2. The Discovery Pipeline (The "Brain")
The engine employs a multi-stage hybrid approach to maximize both precision (reducing false positives) and recall (finding more PII).

### Stage 1: Deterministic Matching (High Precision)
For every column in the source (CSV or SQLite):
1. **Negative Hint Filter**: If the column name matches a "negative hint" (e.g., `created_at` for a DOB rule), the class is immediately excluded.
2. **Name-Hint Scoring**: If the column name matches a predefined "positive hint" (e.g., `email_address`), it receives a `name_score` of 1.0.
3. **Value-Pattern Matching**: Sampled values are checked against compiled regex patterns.
4. **Checksum Validation**: For high-risk IDs (Credit Cards, Aadhaar), a strict checksum (Luhn/Verhoeff) is applied. If the checksum fails, the match is rejected regardless of the regex.
5. **Initial Confidence**: `Confidence = (NameWeight * name_score) + (ValueWeight * value_score)`

### Stage 2: Probabilistic NLP (High Recall)
If the deterministic score is below a high-confidence threshold:
1. **Contextual Analysis**: The system uses **Microsoft Presidio (spaCy NLP)** to analyze the values.
2. **Entity Recognition**: The NLP engine identifies entities (PERSON, LOCATION, etc.) based on the surrounding context and linguistic patterns.
3. **Confidence Boost**: If NLP detects a strong entity, the confidence is boosted, flagging the column for human review.

### Stage 3: Metadata Linking & Gap Analysis
1. **Evidence Inventory**: Findings are linked to declared metadata (Purpose, Retention, Owner).
2. **Gap Detection**: The system flags "Evidence Gaps" where PII is detected but the required metadata is missing.

## 3. Technical Stack
- **Backend**: Python 3.12, FastAPI, Pydantic, Presidio-Analyzer, SQLAlchemy.
- **Frontend**: React 19, Vite, Tailwind CSS, Framer Motion (for animations).
- **Configuration**: YAML-driven rules engine for effortless updates without code changes.

---
*Disclaimer: Privexis Elite provides technical evidence for auditors. It does not make legal or compliance determinations.*
