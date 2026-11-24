# HireMind Cloud Deployment Guide

> [!IMPORTANT]
> **FOR FUTURE REFERENCE ONLY**  
> **Public deployment has NOT happened yet.** HireMind is currently configured, tested, and prepared for GitHub repository hosting. This document outlines the step-by-step procedure for when public cloud deployment is executed in the future.

---

## Target Deployment Architecture

When HireMind is deployed publicly, it is architected to utilize the following cloud providers:

- **Database**: [Neon](https://neon.tech/) — Managed Serverless PostgreSQL 15+
- **Backend API**: [Render](https://render.com/) — Containerized FastAPI Service (Docker)
- **Frontend SPA**: [Vercel](https://vercel.com/) — Global Edge Content Delivery Network (CDN)

```mermaid
sequenceDiagram
    autonumber
    actor DevOps as Engineer / DevOps
    participant Neon as Neon PostgreSQL
    participant Render as Render (Docker Web Service)
    participant Vercel as Vercel (Edge CDN)

    Note over DevOps,Vercel: FUTURE DEPLOYMENT SEQUENCE (NOT CURRENTLY LIVE)
    DevOps->>Neon: 1. Provision PostgreSQL 15+ & copy connection string
    DevOps->>Render: 2. Create Web Service with Dockerfile context 'backend'
    DevOps->>Render: 3. Set environment variables (DATABASE_URL, JWT_SECRET, etc.)
    Render->>Neon: 4. Execute migrations ('alembic upgrade head') & seed questions
    Render->>Render: 5. Container boots with pre-baked SentenceTransformer weights
    DevOps->>Vercel: 6. Deploy frontend with root directory 'frontend' & VITE_API_URL
    Vercel->>Render: 7. Run production smoke tests & verify candidate workflow
```

---

## 1. Database Provisioning: Neon PostgreSQL

### Step 1: Create a Neon Database Project
1. Log in to [Neon Console](https://console.neon.tech/).
2. Create a new project: `hiremind-db`.
3. Select PostgreSQL version: **15** or **16**.
4. Select your preferred cloud region (e.g. `US East (Ohio)`).

### Step 2: Configure Connection String
1. In your Neon dashboard, select **Connection string** format.
2. Select **Pooled connection** or direct connection with `sslmode=require`.
3. The raw connection string format:
   ```
   postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Convert for SQLAlchemy & psycopg v3**:
   Change the URL protocol prefix from `postgresql://` to `postgresql+psycopg://`:
   ```
   postgresql+psycopg://username:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

> [!CAUTION]
> Never commit actual database passwords or connection URLs to Git. Store this connection string securely in Render's encrypted environment variables.

---

## 2. Backend Deployment: Render (Docker Web Service)

### Step 1: Create Web Service
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repository (`HireMind`).

### Step 2: Configure Service Settings
- **Name**: `hiremind-api`
- **Region**: Same geographical region as your Neon database.
- **Branch**: `main`
- **Runtime**: **Docker**
- **Docker Build Context Directory**: `backend`
- **Dockerfile Path**: `backend/Dockerfile`
- **Instance Type**: Starter / Standard (Minimum 1 GB RAM recommended for PyTorch/SentenceTransformers).

### Step 3: Configure Environment Variables
In the **Environment** tab on Render, define the following variables:

| Variable Name | Example / Format | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+psycopg://USER:PASS@HOST/DB?sslmode=require` | Neon PostgreSQL connection string |
| `JWT_SECRET_KEY` | *(Generate a 32+ character random string)* | Cryptographic key for signing JWTs |
| `JWT_ALGORITHM` | `HS256` | JWT signature algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration lifetime |
| `CORS_ORIGINS` | `https://hiremind.vercel.app` | Target Vercel production frontend domain |
| `SQL_ECHO` | `false` | Suppresses query logging in production logs |
| `PORT` | `8000` | (Render dynamically provides this, default 8000 fallback) |

### Step 4: Docker Configuration Details
HireMind includes a pre-configured production Dockerfile at [`backend/Dockerfile`](backend/Dockerfile):
- **Base Image**: `python:3.11-slim` with pinned dependencies from `requirements.txt`.
- **Pre-Cached ML Weights**: The `all-MiniLM-L6-v2` SentenceTransformer model weights (~90MB) are downloaded and cached during the Docker image build stage into `/root/.cache/huggingface`. This prevents cold-start delays and avoids downloading weights over the network at runtime.
- **RAM Conservation**: Starts Gunicorn with **1 Uvicorn worker** (`gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT:-8000}`) to prevent duplicating PyTorch model instances across multiple workers in low-memory environments.
- **Build Exclusions**: [`backend/.dockerignore`](backend/.dockerignore) strips virtual environments, `.env` files, uploads, and local test files from the build image.

### Step 5: Database Migrations & Question Seeding
Configure the **Pre-Deploy Command** field on Render to:
```bash
alembic upgrade head && python seed_questions.py
```
*This command executes automatically before every deployment: it applies all Alembic schema migrations and idempotently seeds all 45 interview questions across 5 engineering roles into the Neon database.*

### Step 6: Resume Persistent Storage
By default, candidate resume uploads are saved to `/app/uploads`. To prevent file loss on ephemeral container restarts:
1. In Render, navigate to **Disks**.
2. Click **Add Disk**.
3. **Mount Path**: `/app/uploads`
4. **Size**: `1 GB` (or larger depending on candidate volume).

---

## 3. Frontend Deployment: Vercel (Edge CDN)

### Step 1: Import Project on Vercel
1. Log in to [Vercel](https://vercel.com/).
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository (`HireMind`).

### Step 2: Configure Project Settings
- **Framework Preset**: **Vite**
- **Root Directory**: Click *Edit* and select **`frontend`**.
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Step 3: Configure Environment Variables
In the **Environment Variables** section on Vercel:

| Variable Name | Value | Purpose |
| :--- | :--- | :--- |
| `VITE_API_URL` | `https://hiremind-api.onrender.com` | Base URL of the live Render FastAPI backend |

### Step 4: Client-Side SPA Rewrites
HireMind includes [`frontend/vercel.json`](frontend/vercel.json) to handle single-page application routing:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
*This ensures client-side routes (`/dashboard`, `/interview`, `/results`, `/profile`, `/resume`) do not return 404 when refreshed in the browser.*

### Step 5: Update Backend CORS
Once Vercel assigns your live domain (e.g. `https://hiremind.vercel.app`):
1. Go to **Render** $\rightarrow$ `hiremind-api` $\rightarrow$ **Environment**.
2. Update `CORS_ORIGINS` to match your Vercel domain:
   ```env
   CORS_ORIGINS=https://hiremind.vercel.app
   ```
3. Save changes to trigger an automated configuration reload.

---

## 4. Final Production Smoke Testing Checklist

When public deployment is executed, verify all systems using this checklist:

- [ ] **Backend Health**: `GET https://your-backend.onrender.com/health` returns `{"status": "healthy"}`.
- [ ] **Database Connectivity**: `GET https://your-backend.onrender.com/db-test` confirms successful connection to Neon.
- [ ] **Candidate Registration**: Register a new user account through the Vercel web UI.
- [ ] **Authentication**: Log in and verify that the JWT token is stored and authenticated headers are attached.
- [ ] **Resume Upload & Parsing**: Upload a PDF resume on `/resume`; verify skills are extracted and semantic similarity matches against the target role.
- [ ] **Mock Interview Workflow**: Complete an adaptive interview session (Technical, Problem Solving, and Behavioral questions); verify question progression and real-time score feedback.
- [ ] **Career Readiness Report**: Verify that the generated readiness report displays all 6 dimensions with structured tier recommendations on `/results`.
- [ ] **Dashboard Analytics**: Confirm that the `/dashboard` page populates overview cards, the 6-dimension `SkillRadarChart`, performance trends, and category breakdown bars.
- [ ] **Client Routing Persistence**: Refresh the browser while on `/dashboard` or `/interview` to confirm Vercel rewrites do not return 404.

---

## 5. Security Summary

- **Zero Secrets in Git**: No database URLs, passwords, or JWT secrets are stored in Git; all secrets are managed via cloud provider dashboards.
- **`.gitignore` Protection**: Excludes `.env`, `backend/.env`, `frontend/.env.production`, `uploads/`, `venv/`, `node_modules/`, and temporary cache directories.
- **Zero External AI Costs**: Deep learning models run entirely on the local container CPU via PyTorch, requiring no paid external AI API subscriptions.
