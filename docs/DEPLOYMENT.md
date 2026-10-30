# Deployment Guide — Privexis

This project consists of a high-performance **FastAPI backend** (`api/main.py`) and a modern **React + Vite frontend** (`frontend/`).

---

## Recommended Deployment Setup

| Component | Recommended Platform | Alternative | Cost |
|---|---|---|---|
| **Backend API** | [Render](https://render.com) | [Railway](https://railway.app) / [Fly.io](https://fly.io) | Free Tier |
| **Frontend UI** | [Vercel](https://vercel.com) | [Netlify](https://netlify.com) / [Cloudflare Pages](https://pages.cloudflare.com) | Free Tier |

---

## Step 1: Deploy Backend on Render

1. Push your repository to **GitHub**.
2. Go to [dashboard.render.com](https://dashboard.render.com) and click **New +** → **Web Service**.
3. Connect your GitHub repository: `A3-PS019-TC155`.
4. Configure the service settings:
   - **Name**: `infynex-privexis-api`
   - **Region**: Nearest to you (e.g. Singapore or Frankfurt)
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn api.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`
5. Click **Create Web Service**.
6. Once deployed, Render will provide a public URL like:
   `https://infynex-privexis-api.onrender.com`
7. Test it by opening:
   `https://infynex-privexis-api.onrender.com/api/health` → `{"status": "healthy"}`

---

## Step 2: Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and click **Add New...** → **Project**.
2. Import your GitHub repository: `A3-PS019-TC155`.
3. Configure the project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand **Environment Variables** and add:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: Your Render backend URL (e.g., `https://infynex-privexis-api.onrender.com`)
5. Click **Deploy**.
6. Vercel will build and assign you a live production domain (e.g., `https://infynex-sentinel.vercel.app`).

---

## Alternative 1: 1-Click Railway Deployment (Fastest, No Cold Starts)

If you prefer **Railway** (which has zero cold-start delay):
1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
2. For backend: Root directory `/`, start command `uvicorn api.main:app --host 0.0.0.0 --port $PORT`.
3. Generate a domain under **Settings** → **Networking**.
4. Set that domain as `VITE_API_BASE_URL` in Vercel!

---

## Alternative 2: Docker / Container Deployment

A simple `Dockerfile` if you want to deploy to AWS, GCP Cloud Run, or Fly.io:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

