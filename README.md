<div align="center">

# Privexis

### Personal-Data Discovery and Privacy Evidence Inventory

Team **Infynex** · AIORI Hackathon 3 · Problem Statement **PS-019** (Cybersecurity)

[![Live demo](https://img.shields.io/badge/LIVE%20DEMO-OPEN%20APP-0F766E?style=flat-square&logo=vercel&logoColor=white)](https://a3-ps-019-tc-155.vercel.app/)
[![Repo](https://img.shields.io/badge/SOURCE-GITHUB-24292F?style=flat-square&logo=github&logoColor=white)](https://github.com/aiori-hackathon/A3-PS019-TC155)
![Python](https://img.shields.io/badge/Python-3.11-4F46E5?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-0F766E?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-frontend-0369A1?style=flat-square&logo=react&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-CSS-7C3AED?style=flat-square&logo=tailwindcss&logoColor=white)
![Track](https://img.shields.io/badge/Track-Cybersecurity-B45309?style=flat-square)

</div>

---

Try the deployed web app: [![Open Privexis](https://img.shields.io/badge/OPEN-PRIVEXIS%20WEB%20APP-0F766E?style=flat-square)](https://a3-ps-019-tc-155.vercel.app/)

<!-- Add these once you have the links, then delete this comment:
Watch the complete walkthrough of Privexis on YouTube: [![YouTube](https://img.shields.io/badge/VIDEO-WALKTHROUGH-BE123C?style=flat-square&logo=youtube&logoColor=white)](YOUTUBE_URL)
-->

---

## What it does

Privexis scans **CSV files and SQLite databases**, finds candidate personal-data columns in five classes, and links each one to its declared **purpose, retention and owner**. It then reports what evidence is missing.

| Class | How it is recognised |
|---|---|
| `NAME` | Column-name hints plus a person-name shape check (capitalised words, organisation words excluded) |
| `EMAIL` | Hints plus an RFC 5322-style syntax check |
| `PHONE` | Hints plus Indian mobile (`+91`, 10 digits starting 6-9) or international number checks |
| `GOVT_ID` | Hints plus **Verhoeff checksum** (Aadhaar-style) or PAN format |
| `DOB` | Hints plus a calendar-valid date between 1900 and today |

For every column, `confidence = name_weight × name-hint match + value_weight × share of sampled values that pass the validator`. Weights, hints and thresholds live in [`config/rules.yaml`](config/rules.yaml), so you can change detection without touching code.

> **Scope:** the output is technical evidence for human review. Privexis does **not** make a legal or compliance determination, does not decide a lawful basis, and does not infer how data flows between systems.

## Pipeline

```
CSV / SQLite ─► connectors ─► sampler ─► rule engine ─► linker ─► inventory + gaps
                (read-only)   (≤50 vals)  (hint + value)  (metadata.yaml + checklist.yaml)
```

1. **Sample** a bounded number of values per column.
2. **Score** each column with name hints and strict value validators.
3. **Link** flagged columns to `config/metadata.yaml` and check them against `config/checklist.yaml` (purpose, retention, owner).
4. **Report** the inventory with evidence, masked sample values and the gaps found.

See [`PSEUDOCODE.md`](PSEUDOCODE.md) for the core algorithm.

## Web app

| Page | Purpose |
|---|---|
| Command Center | Totals, class breakdown and gap summary of the latest scan |
| Discovery Scanner | Upload CSV/SQLite files (plus an optional metadata file) or run the bundled demo |
| Evidence Inventory | Per-column evidence: scores, masked samples, declared purpose / retention / owner |
| Evidence Gaps | Columns with missing metadata; fill them in from the UI |
| Rule Engine | The active detection rules, read from `config/rules.yaml` |
| Accuracy & Metrics | Per-class precision and recall on the labelled sets |
| Try to Fool It | Hard cases that test whether name and value evidence hold up |

## Accuracy

Measured per column on labelled data, with the code in this repository (`/api/accuracy`, the Accuracy page, or `pytest tests/test_accuracy.py`):

| Set | Columns | Precision | Recall | F1 | What it tells you |
|---|---|---|---|---|---|
| Main (`data/`) | 22 | 1.00 | 1.00 | 1.00 | Hand-labelled. Rules were adjusted while looking at it, so this is **not** a generalisation measure |
| Holdout (`data/holdout/`) | 21 | 1.00 | 1.00 | 1.00 | Hand-labelled. Also seen while tuning |
| **Unseen generated set** (`data/stress/sealed/`) | 180 | **0.89** | **0.82** | **0.86** | Different names and column vocabulary from the set used for tuning (`data/stress/tune/`). **The fairest estimate here**, though its results were looked at twice during development |

The unseen set is produced by `scripts/generate_stress.py` (fixed seed) and includes deliberately hard columns: neutral names (`tenant`, `payee`), order numbers and SKU-like codes, hire dates, JSON profile columns, mixed contact columns, free-text notes, empty columns, and Latin-1 / semicolon-delimited files. Expect real-world data to land near the unseen figures, not the 1.00 rows.

Where it still fails (visible on the Accuracy page): person names under neutral headers go to "needs review" instead of being flagged, and PAN-shaped product codes can be flagged unless `strict_pan: true` is set in `config/rules.yaml`.

## Run it locally

```bash
# Backend (Python 3.11+)
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -e . -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Frontend (Node 20+), in a second terminal
cd frontend
npm install
npm run dev                          # http://localhost:5173 (proxies /api to :8000)
```

Command line:

```bash
privexis scan --data data --config config --out reports
privexis template            # writes a metadata template
```

Tests:

```bash
pip install -r requirements-dev.txt
pytest
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Liveness check |
| POST | `/api/scan` | Upload CSV/SQLite files (max 10 MB each) and scan them |
| POST | `/api/scan-demo` | Scan the bundled sample data |
| GET | `/api/accuracy` | Precision / recall on the three evaluation sets |
| GET | `/api/rules` | Active detection rules |
| GET | `/api/demos` | Hard-case demonstrations |
| POST | `/api/metadata/update` | Record purpose / retention / owner for a column |

## Deployment

| Part | Host | Notes |
|---|---|---|
| Frontend | Vercel | Root directory `frontend`. Set `VITE_API_BASE_URL` to the backend URL |
| Backend | Render (Docker) | `uvicorn api.main:app`. Set `CORS_ORIGINS` for any extra frontend origin |

The deployed frontend origin (`https://a3-ps-019-tc-155.vercel.app`) is already allowed by the API's CORS list.

## Repository layout

```
api/            FastAPI app
src/privexis/   engine, validators, sampler, linker, pipeline, evaluator, CLI
config/         rules.yaml, checklist.yaml, metadata.yaml
data/           sample data, hand-labelled answer keys, generated unseen set
scripts/        generate_stress.py (regenerates the unseen set)
frontend/       React + Vite + Tailwind UI
tests/          pytest suite
```

## Known limitations

- Sampling: only a bounded number of values per column is checked, so rare values in large tables can be missed.
- Columns with neutral names (for example `tenant`, `payee`) rely on value shape alone; person names there are sent to review, not flagged.
- A PAN-shaped product code can be flagged as a government ID (set `strict_pan: true` to require a real holder-type letter, at the cost of missing synthetic PANs with arbitrary letters).
- Name detection is heuristic. It uses shape rules, not a trained model.
- Metadata edits made in the web app are written to the server's `config/metadata.yaml`. Treat the hosted demo as single-user.

## Team Infynex

| Name | Role | GitHub |
|---|---|---|
| Vibhakar Gangwar | Team Lead | [@vibhakargangwar](https://github.com/vibhakargangwar) |
| Vaibhav Tiwari | Member | [@vaibhaavtiwarii](https://github.com/vaibhaavtiwarii) |
| Aditya Pandey | Mentor | [@pandeyOnGitt](https://github.com/pandeyOnGitt) |

## License

MIT
