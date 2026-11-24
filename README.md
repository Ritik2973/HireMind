# HireMind

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.14+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

### **AI-Based Adaptive Interview and Career Readiness Analyzer Using Deep Learning**

An intelligent, explainable technical hiring platform that combines NLP resume parsing, dynamic adaptive mock interviews, and multi-dimensional career readiness scoring using local deep learning embeddings.

[Features](#key-features) • [Architecture](#system-architecture) • [Getting Started](#local-installation-instructions-windows) • [Testing](#running-automated-tests) • [API Docs](#api-documentation) • [Future Roadmap](#future-enhancements)

</div>

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Folder Structure](#project-folder-structure)
- [Screenshots & UI Showcase](#screenshots--ui-showcase)
- [Prerequisites](#prerequisites)
- [Local Installation Instructions (Windows)](#local-installation-instructions-windows)
- [Environment Variable Configuration](#environment-variable-configuration)
- [Starting Backend & Frontend](#starting-backend--frontend)
- [Running Automated Tests](#running-automated-tests)
- [API Documentation (Swagger UI)](#api-documentation-swagger-ui)
- [Future Enhancements](#future-enhancements)
- [Deployment Status](#deployment-status)
- [Contributors](#contributors)
- [License](#license)

---

## Project Overview

**HireMind** is an enterprise-grade recruitment and career readiness assessment system. It bridges the gap between candidate academic preparation and industry hiring standards through a data-driven, reproducible evaluation methodology.

Rather than relying on arbitrary large language model scoring or static question banks, HireMind couples an **Adaptive Interview Engine** with an **in-memory Sentence Transformer embedding model** (`all-MiniLM-L6-v2`) to provide:
1. Deterministic semantic evaluation of candidate responses against benchmark concept rubrics.
2. Dynamic difficulty scaling (EASY $\leftrightarrow$ MEDIUM $\leftrightarrow$ HARD) adapting in real time across Technical, Problem Solving, and Behavioral categories.
3. A holistic 6-dimension Career Readiness Analyzer delivering actionable, tiered feedback for aspiring engineers.

---

## Problem Statement

Traditional hiring assessment and interview preparation tools suffer from several fundamental limitations:
- **Arbitrary AI Hallucination**: Generative AI scoring prompts drift widely across iterations, generating unpredictable numbers without mathematical grounding.
- **Static, One-Size-Fits-All Assessments**: Standard question banks fail to adapt to a candidate's demonstrated competency level during the interview.
- **Disconnected Resume Insights**: Resume parsers list extracted keywords but rarely benchmark how well a candidate's background matches specific engineering roles.
- **Lack of Actionable Feedback**: Candidates receive vague rejection emails or binary pass/fail grades without diagnostic breakdowns of where their knowledge fell short.

HireMind solves these problems by providing an open, deterministic, explainable evaluation pipeline built on mathematical semantic similarity, concept keyword coverage, and weighted dimensional analysis.

---

## Project Objectives

1. **Deterministic & Explainable Scoring**: Eliminate hallucinated grades by grounding evaluations in cosine similarity, concept coverage rubrics, and published mathematical formulas.
2. **Adaptive Interview Experience**: Progress candidates dynamically through 3 calibrated interview stages across 5 supported engineering roles.
3. **Multi-Dimensional Readiness Modeling**: Measure and display readiness across 6 distinct dimensions: Technical Knowledge, Problem Solving, Communication, Behavioral Readiness, Resume-Skill Alignment, and Consistency.
4. **Zero-Cost, Local Deep Learning**: Run semantic vector embeddings directly on CPU via PyTorch, eliminating third-party AI API subscription costs and latency.
5. **Secure, Multi-Tenant Architecture**: Enforce strict cross-user data isolation, Argon2id password hashing, and Bearer token JWT authentication.

---

## Key Features

### 1. User Authentication & Profile Management
- Secure password hashing utilizing modern **Argon2id** through `pwdlib`.
- Stateless **JWT authentication** (HMAC-SHA256) with automatic expiration and token revocation handling.
- Profile management allowing candidates to configure their target software engineering role.

### 2. Resume Upload & Parsing
- Fast, secure PDF upload with client and server MIME validation and 5MB size guards.
- In-memory PDF text extraction via `pypdf`.
- Automated taxonomy skill extraction covering programming languages, frameworks, databases, and DevOps tooling.

### 3. AI-Powered Resume Analysis
- Pre-trained `all-MiniLM-L6-v2` dense vector embedding model producing 384-dimensional semantic vectors.
- Cosine similarity matching against curated target job role profiles (Software Engineer, Data Scientist, ML Engineer, Backend Developer, Frontend Developer).

### 4. Adaptive Mock Interviews
- Dynamic 3-stage question sequences covering **Technical Knowledge**, **Problem Solving**, and **Behavioral Readiness**.
- Real-time difficulty calibration (EASY $\leftrightarrow$ MEDIUM $\leftrightarrow$ HARD) based on candidate performance on preceding questions.

### 5. AI-Based Answer Evaluation
- Semantic similarity calculation comparing candidate responses with expert expected answers.
- Concept keyword coverage verification against multi-concept rubrics.
- Automated completeness checks and contextual feedback generation.

### 6. Career Readiness Reports
- Comprehensive report generated from stored interview responses and resume data using a strict mathematical formula:
  $$\text{Overall Score} = (\text{Tech} \times 0.25) + (\text{PS} \times 0.20) + (\text{Comm} \times 0.20) + (\text{Beh} \times 0.15) + (\text{Resume} \times 0.10) + (\text{Perf} \times 0.10)$$
- Actionable recommendations categorized across 4 standardized readiness tiers:
  - **Needs Substantial Improvement** (< 50)
  - **Developing** (50 – 69)
  - **Solid** (70 – 84)
  - **Strong** (85 – 100)

### 7. Candidate Dashboard & Analytics
- Visual dashboard built in React and Tailwind CSS.
- 5 custom SVG visualization components:
  - **SkillRadarChart**: 6-axis radar visualization of all career readiness dimensions.
  - **PerformanceTrendChart**: Historical progression tracking across interview sessions.
  - **CategoryBreakdown**: Visual percentage progress bars for core categories.
  - **RecentInterviewsTable**: Session history with status badges, dates, and navigation.
  - **SkillTagsCloud**: Extracted resume skills presented in interactive tag badges.
- First-time user guided empty state onboarding (`DashboardEmptyState.jsx`).

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, Tailwind CSS v4, React Router DOM v7, Lucide Icons, Axios |
| **Backend** | Python 3.11+, FastAPI 0.141, Uvicorn, Gunicorn |
| **Database & ORM** | PostgreSQL 15+, SQLAlchemy 2.0, Alembic (Migrations), Psycopg v3 |
| **AI / Deep Learning** | Sentence Transformers (`all-MiniLM-L6-v2`), PyTorch, NumPy, SciPy |
| **Security & Auth** | Argon2id (`pwdlib`), PyJWT (`HS256`), OAuth2 Bearer Tokens |
| **Document Processing**| `pypdf`, `fpdf2` |
| **Containerization** | Docker, Multi-Stage Python Slim Image |

---

## System Architecture

```mermaid
flowchart TD
    subgraph FrontendSPA["Frontend Client (React 19 + Vite)"]
        UI["Candidate UI (Dashboard, Interview, Results, Resume)"]
        AuthContext["AuthContext (JWT in localStorage)"]
        AxiosClient["Axios Client (Bearer Interceptor)"]
        UI --> AxiosClient
        AuthContext --> AxiosClient
    end

    subgraph FastAPIGateway["Backend API Gateway (FastAPI)"]
        CORS["CORS Middleware"]
        AuthGuard["JWT Auth Dependency (get_current_user)"]
        ExceptionHandler["Global Exception Sanitizer"]
        CORS --> AuthGuard --> ExceptionHandler
    end

    subgraph ServiceLayer["Core Domain Services"]
        ResumeService["Resume Parser & Taxonomy Extractor"]
        MLService["ML Vector Embedding (all-MiniLM-L6-v2)"]
        InterviewService["Adaptive Interview Engine"]
        EvaluatorService["AI Answer Evaluator"]
        ReadinessService["Career Readiness Analyzer"]
        AnalyticsService["Dashboard Analytics Service"]
    end

    subgraph DatabaseLayer["Data & File Persistence"]
        Postgres[("PostgreSQL Database (Neon / Local)")]
        DiskStorage[("Persistent Volume Mount (/app/uploads)")]
    end

    AxiosClient -->|HTTPS REST API| FastAPIGateway
    ExceptionHandler --> ServiceLayer
    ResumeService --> DiskStorage
    ServiceLayer --> Postgres
```

---

## Project Folder Structure

```
HireMind/
├── backend/
│   ├── alembic/                 # Database schema migrations & env.py
│   │   └── versions/            # Sequential migration revisions
│   ├── database/
│   │   └── connection.py        # SQLAlchemy engine, session maker, pool_pre_ping
│   ├── ml/
│   │   ├── embeddings/          # SentenceTransformer lazy loader & vector encoder
│   │   ├── profiles/            # Target role profiles & benchmark definitions
│   │   └── services/            # Cosine similarity semantic analysis
│   ├── models/                  # SQLAlchemy ORM database models
│   │   ├── interview.py         # InterviewSession, InterviewQuestion, InterviewResponse
│   │   ├── readiness.py         # CareerReadinessReport model
│   │   ├── resume.py            # Resume model
│   │   └── user.py              # User model
│   ├── routers/                 # FastAPI API route controllers
│   │   ├── analytics.py         # GET /analytics/dashboard
│   │   ├── auth.py              # POST /auth/register, /auth/login, /auth/me
│   │   ├── career_readiness.py  # POST /career-readiness/generate, GET /{id}
│   │   ├── interview.py         # POST /interviews/start, POST /{id}/answer
│   │   ├── ml.py                # POST /ml/analyze-resume
│   │   ├── resume.py            # POST /resumes/upload, GET /resumes/{id}
│   │   └── user.py              # GET /users/me, PUT /users/me
│   ├── schemas/                 # Pydantic v2 data validation schemas
│   ├── security/                # Argon2 password hashing & JWT token verification
│   ├── services/                # Core business logic & calculation services
│   ├── uploads/                 # Local candidate uploaded resume storage
│   ├── .dockerignore            # Docker build ignore rules
│   ├── .env.example             # Safe template for backend environment variables
│   ├── alembic.ini              # Alembic migration configuration
│   ├── Dockerfile               # Production multi-stage Docker container
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   ├── requirements.txt         # Pinned Python package dependencies
│   ├── seed_questions.py        # Idempotent question seeder (45 questions)
│   └── test_*.py                # Automated backend test suites
├── frontend/
│   ├── public/
│   │   ├── _redirects           # Netlify SPA routing rewrite rule
│   │   └── favicon.svg
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js        # Configured Axios client with VITE_API_URL
│   │   ├── components/
│   │   │   ├── analytics/       # Radar chart, trend chart, breakdowns, tables
│   │   │   ├── layout/          # Navbar, Footer
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # Authentication provider & user session state
│   │   ├── pages/               # Dashboard, Interview, Results, Resume, Login, Register
│   │   ├── App.jsx              # Client-side route declarations
│   │   └── main.jsx
│   ├── package.json             # Frontend dependencies & npm scripts
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   ├── vercel.json              # Vercel SPA routing rewrite rule
│   └── vite.config.js           # Vite bundler configuration
├── .gitignore                   # Root Git ignore rules (secrets, venv, node_modules)
├── DEPLOYMENT.md                # Cloud deployment runbook (Future reference)
└── README.md                    # Project documentation
```

---

## Screenshots & UI Showcase

*(Screenshots can be placed in `docs/screenshots/`)*

| Analytics Dashboard | Six-Dimension Skill Radar |
| :---: | :---: |
| ![Dashboard Preview](https://via.placeholder.com/600x350/0f172a/38bdf8?text=Candidate+Analytics+Dashboard) | ![Skill Radar Preview](https://via.placeholder.com/600x350/0f172a/a855f7?text=6-Dimension+Skill+Radar+Chart) |

| Adaptive Interview Flow | Career Readiness Report |
| :---: | :---: |
| ![Interview Session](https://via.placeholder.com/600x350/0f172a/22c55e?text=Adaptive+Mock+Interview+Screen) | ![Career Readiness Report](https://via.placeholder.com/600x350/0f172a/eab308?text=Career+Readiness+Diagnostic+Report) |

---

## Prerequisites

Before setting up HireMind locally on Windows, ensure the following are installed:
- **Windows 10 or 11** (64-bit)
- **Python 3.11+** ([python.org](https://www.python.org/downloads/)) — *Check "Add Python to PATH" during installation*
- **Node.js 18+ & npm** ([nodejs.org](https://nodejs.org/))
- **PostgreSQL 14+** ([postgresql.org](https://www.postgresql.org/download/windows/)) running locally on port 5432, or a free cloud PostgreSQL database (e.g. [Neon](https://neon.tech/))
- **Git** ([git-scm.com](https://git-scm.com/))

---

## Local Installation Instructions (Windows)

Open **PowerShell** or **Command Prompt** as Administrator:

### 1. Clone the Repository
```powershell
git clone https://github.com/your-username/HireMind.git
cd HireMind
```

### 2. Backend Virtual Environment & Dependencies
```powershell
# Navigate into backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
# (Or in Command Prompt: venv\Scripts\activate.bat)

# Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Frontend Dependencies
```powershell
# Navigate into frontend directory from root
cd ..\frontend

# Install npm dependencies
npm install
```

---

## Environment Variable Configuration

Create a `.env` file in the `backend/` directory using the provided safe template:

```powershell
cd ..\backend
Copy-Item .env.example .env
```

### Safe Backend `.env` Template:
```env
# Database Connection (Local PostgreSQL or Neon Cloud)
DATABASE_URL=postgresql+psycopg://postgres:your_local_password@localhost:5432/hiremind

# JWT Secret Key (Generate a random 32+ character key)
JWT_SECRET_KEY=your_secure_random_secret_key_minimum_32_bytes_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Allowed CORS Origins (comma-separated frontend URLs)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# SQLAlchemy Engine Query Logging (false recommended)
SQL_ECHO=false
```

---

## Starting Backend & Frontend

### 1. Initialize the Database Schema & Questions
From the `backend/` directory with `venv` activated:
```powershell
# Apply Alembic schema migrations
alembic upgrade head

# Seed all 45 interview questions across 5 engineering roles
python seed_questions.py
```

### 2. Start the Backend API Server
```powershell
# From backend/ directory with venv activated:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*The FastAPI server will start at: `http://localhost:8000`.*

### 3. Start the Frontend Development Server
Open a **new terminal window** in the `frontend/` directory:
```powershell
cd frontend
npm run dev
```
*The web interface will launch at: `http://localhost:5173`.*

---

## Running Automated Tests

HireMind includes automated unit, regression, security, and end-to-end integration test suites:

From the `backend/` directory with `venv` activated:

```powershell
# 1. Run Complete End-to-End Workflow Integration Test (10/10 Steps)
python test_e2e_flow.py

# 2. Run Security Audit & Attack Simulation Test Suite (7/7 Tests)
python test_security_audit.py

# 3. Run Dashboard & Analytics API Test Suite (6/6 Tests)
python test_analytics_api.py

# 4. Run Career Readiness Report API Test Suite (8/8 Tests)
python test_career_readiness_api.py

# 5. Run Career Readiness Mathematical Calculation Tests
python test_career_readiness.py
```

### Frontend Build & Lint Checks
From the `frontend/` directory:
```powershell
# Production bundle build test
npm run build

# Code linting check
npm run lint
```

---

## API Documentation (Swagger UI)

FastAPI automatically serves interactive, self-documenting OpenAPI endpoints:

- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Interactive ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints Quick Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/auth/register` | Register a new candidate account | No |
| `POST` | `/auth/login` | Authenticate candidate & obtain JWT token | No |
| `GET` | `/users/me` | Retrieve authenticated candidate profile | Yes (Bearer) |
| `PUT` | `/users/me` | Update candidate name or target engineering role | Yes (Bearer) |
| `POST` | `/resumes/upload` | Upload PDF resume, extract text & skills | Yes (Bearer) |
| `GET` | `/resumes/{id}` | Retrieve parsed resume metadata | Yes (Bearer) |
| `POST` | `/ml/analyze-resume` | Compute semantic similarity against target role | Yes (Bearer) |
| `POST` | `/interviews/start` | Start adaptive interview session | Yes (Bearer) |
| `GET` | `/interviews/{id}` | Retrieve session status & current question | Yes (Bearer) |
| `POST` | `/interviews/{id}/answer` | Submit answer, evaluate response, advance difficulty | Yes (Bearer) |
| `POST` | `/career-readiness/generate` | Generate deterministic Career Readiness Report | Yes (Bearer) |
| `GET` | `/career-readiness/{id}` | Retrieve Career Readiness Report by ID | Yes (Bearer) |
| `GET` | `/career-readiness/latest` | Retrieve candidate's latest readiness report | Yes (Bearer) |
| `GET` | `/analytics/dashboard` | Aggregated interview, category, and readiness stats | Yes (Bearer) |
| `GET` | `/health` | Container healthcheck endpoint | No |

---

## Future Enhancements

- **Voice & Speech-to-Text Interface**: Real-time voice interview mode using local Whisper models.
- **Video & Engagement Feedback**: Non-invasive pacing, confidence, and articulation diagnostics.
- **In-Browser Coding Playground**: Embedded Monaco code editor with sandboxed execution for live coding questions.
- **Cloud Object Storage (S3/Cloudflare R2)**: Scalable object storage for uploaded resume PDFs across distributed clusters.
- **Hiring Manager & Recruiter Portal**: Verified candidate readiness reports with shareable digital verification links.

---

## Deployment Status

> [!NOTE]
> **HireMind is currently prepared for GitHub repository hosting.**
> Public cloud deployment (via Vercel, Render, and Neon) will occur in a future phase.
> For future production setup instructions, refer to [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## Contributors

<!-- You can add your GitHub profile and contributors here -->
- **Project Lead & Developer**: [Your Name / GitHub Profile](https://github.com/your-username)
- Contributions, issues, and feature requests are welcome!

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
