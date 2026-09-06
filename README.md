# Aegis — AI-Powered Cyber Threat Detection Framework

An end-to-end system that detects network intrusions in real time using a hybrid
machine learning pipeline, and surfaces alerts through a full-stack security
dashboard ("Aegis"). Built on the NSL-KDD intrusion detection benchmark.

## Overview

Network traffic records are scored by a two-model ensemble:

- A **supervised XGBoost classifier** that categorizes traffic into 5 classes:
  `normal`, `dos` (denial of service), `probe` (reconnaissance/scanning),
  `r2l` (remote-to-local access), and `u2r` (user-to-root privilege escalation).
- An **unsupervised Isolation Forest**, trained only on benign traffic, that
  flags statistically anomalous records the classifier alone would miss —
  a safety net for unknown/zero-day-style attacks.

When the classifier predicts "normal" but the anomaly detector disagrees, the
record is escalated to a `suspicious` verdict. Every verdict is assigned a
severity (Critical / High / Medium / Low) and persisted as an alert.

## Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌───────────────────┐      ┌──────────────┐
│  Simulator   │ ───▶ │   FastAPI backend │ ───▶ │  ML Ensemble       │ ───▶ │  PostgreSQL   │
│ (replay NSL- │      │  /api/ingest      │      │  XGBoost +         │      │  (alerts,     │
│  KDD stream) │      │  /api/alerts      │      │  Isolation Forest  │      │  users,       │
└─────────────┘      │  /api/auth        │      └───────────────────┘      │  stats)       │
                      │  /api/stats       │                                 └──────────────┘
                      │  /api/model       │
                      └─────────┬────────┘
                                │
                                ▼
                      ┌───────────────────┐
                      │  React dashboard   │
                      │  (Aegis UI)        │
                      └───────────────────┘
```

## Project structure

```
AIML-main/
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/             # Route handlers: auth, ingest, alerts, stats, model
│   │   ├── core/            # Security (JWT, password hashing)
│   │   ├── db/              # SQLAlchemy models and session management
│   │   ├── ml/              # Preprocessing, ensemble logic, inference engine, training scripts
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   └── main.py          # App entrypoint
│   ├── tests/                # Backend test suite
│   └── requirements.txt
├── frontend/                # React + Vite + Tailwind dashboard
│   └── src/
│       ├── pages/           # Login, Dashboard, AlertsFeed, ModelMetrics
│       └── api/             # API client
├── ml/
│   ├── data/                 # NSL-KDD train/test CSVs + download script
│   ├── models/                # Trained model artifacts (.joblib) + metrics.json
│   └── evaluation_report.md   # Latest model evaluation results
├── simulator/
│   └── replay_stream.py      # Replays NSL-KDD test records against the live API
├── docker-compose.yml
└── threat_db.sqlite          # Local SQLite DB (dev convenience)
```

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL (SQLite for local dev), JWT auth
- **ML:** scikit-learn, XGBoost, pandas, joblib
- **Frontend:** React 19, Vite, Tailwind CSS, Recharts, lucide-react
- **Infra:** Docker Compose

## Getting started

### 1. Get the dataset
```bash
cd ml/data
python download_nsl_kdd.py
```

### 2. Train the models
```bash
cd backend/app/ml
python train_supervised.py
python train_anomaly.py
```
This produces `preprocessor.joblib`, `supervised.joblib`, `anomaly.joblib`, and
`metrics.json` under `ml/models/`, plus `ml/evaluation_report.md`.

### 3. Run with Docker Compose
```bash
docker-compose up --build
```
- Backend API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173

### 4. Run locally without Docker
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### 5. Simulate live traffic
```bash
cd simulator
python replay_stream.py --url http://localhost:8000/api --rate 2 --batch 1
```
This registers/logs in an admin user automatically and streams NSL-KDD test
records to the ingestion endpoint, printing alerts as they're generated.

## API summary

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register` | POST | Register a new user (first user becomes admin) |
| `/api/auth/login` | POST | Obtain a JWT access token |
| `/api/ingest` | POST | Score a single traffic record |
| `/api/ingest/batch` | POST | Score a batch of traffic records |
| `/api/alerts` | GET | List alerts, filterable by status/severity/label/source |
| `/api/alerts/{id}` | PATCH | Update alert status/assignment |
| `/api/stats/overview` | GET | Dashboard summary stats |
| `/api/model/metrics` | GET | Latest model evaluation metrics |

## Current model performance

See [`ml/evaluation_report.md`](ml/evaluation_report.md) for full details.

- Overall accuracy: **77.6%**
- ROC-AUC (macro, one-vs-rest): **0.949**
- False positive rate: **2.8%**

Performance is strong on `normal` and `dos` traffic but notably weak on rare
attack classes (`r2l`, `u2r`) due to class imbalance in NSL-KDD — see
[Limitations](#limitations--future-work) below.

## Limitations & future work

- **Class imbalance:** R2L and U2R attacks are under-detected (recall of 8.8%
  and 3.5% respectively). Future work: class weighting, SMOTE-based
  resampling, or focal loss.
- **Security hardening:** the JWT secret and CORS policy in `docker-compose.yml`
  are set for local development only and must be replaced before any
  production deployment.
- **Ensemble validation:** the anomaly-detector override is not yet evaluated
  in isolation to confirm it catches attacks the classifier misses.

## License

Add a license of your choice (e.g. MIT) here.
