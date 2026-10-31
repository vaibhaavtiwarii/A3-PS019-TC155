# Privexis: Personal-Data Discovery and Privacy Evidence Inventory

Team Infynex | AIORI Hackathon 3 | PS-019 (Cybersecurity)

**Live demo:** https://a3-ps019-tc155-aiori.streamlit.app/ 

Privexis scans CSV and SQLite data, finds candidate personal-data fields across five classes (name, email, phone, government ID, date of birth), links each to its declared purpose and retention metadata, checks it against a configurable evidence checklist, and flags what is missing.

> **Scope:** the output is technical evidence for human review. Privexis makes no legal or compliance determination, never decides a lawful basis, and does not infer how data flows between systems.

## Evaluation Results

| Set | Precision | Recall | F1 | Notes |
|-----|-----------|--------|-----|-------|
| Main (hand-labelled, tuned-on) | 0.89 | 0.84 | **0.86** | Tuned on — does not measure generalisation |
| Holdout (sealed, unseen) | 0.78 | 0.72 | **0.75** | True generalisation measure |

> **Note:** The hand-labelled sets were used during development (tuned-on). Only the sealed holdout set measures generalisation. On the holdout set, the engine correctly defers neutral-name columns (tenant, payee) to "needs review" and only flags PAN-shaped `item_code` columns as false positives when `strict_pan` is disabled.

## Quick start

```bash
# Backend
python -m venv .venv
.venv/Scripts/activate            # Linux/Mac: source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
uvicorn api.main:app --reload --port 8000

# Frontend (in separate terminal)
cd frontend
npm install
npm run dev
```

## Deployment

### Backend (FastAPI) → Render
Render is the easiest for FastAPI. It handles Docker, environment variables, and has a generous free tier.

1. Create `Dockerfile` (already added).
2. Push to GitHub.
3. Connect Render to repo.
4. Set build command: `docker build -t render-api . && docker run -p 8000:8000 render-api`
5. Set env var `VITE_API_BASE_URL` in Render Dashboard.
6. Deploy.

### Frontend → Vercel
Vercel is best for Vite/React projects — zero-config, automatic SSL.

1. Push to GitHub.
2. Connect Vercel to repo.
3. Configure env var `VITE_API_BASE_URL` (backend URL).
4. Deploy — Vercel auto-builds.

### Alternative: Cloudflare Pages (Fastest Free)
- Connect Git repo.
- Build command: `npm run build`.
- Output dir: `dist`.
- Deploy.
- Add custom domain via CNAME.

## CI/CD (GitHub Actions)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Deploy to Render
        run: |
          curl -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploy" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json"
        env:
          RENDER_SERVICE_ID: ${{ secrets.RENDER_SERVICE_ID }}
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Build
        run: cd frontend && npm run build
      - name: Deploy to Vercel
        run: |
          npx vercel --prod --yes
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

Add secrets to GitHub repo: `RENDER_SERVICE_ID`, `RENDER_API_KEY`, `VERCEL_TOKEN`.

## Environment Variables

In Render Dashboard and Vercel Dashboard, set:
- `VITE_API_BASE_URL`: backend URL (e.g., `https://your-api.onrender.com`)

## Requirements

- Python 3.11
- Node.js 20+
- Docker (for Render)
- GitHub account
- Render account (free)
- Vercel account (free)

## License

MIT
