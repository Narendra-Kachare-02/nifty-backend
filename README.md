# Backend (Django + DRF + Celery)

## What this does
- Fetches **real NIFTY 50** data from NSE.
- Saves snapshots into Postgres during market hours.
- Serves a polling API for the frontend:
  - `GET /api/nifty/latest/`
  - `GET /api/nifty/series/?range=15M|30M|1H|1D`
  - `GET /api/nifty/option-chain/latest/?expiryDate=...`

## Setup

### 1) Create `.env`
Create `backend/.env` with your DB + secrets (do **not** commit it).

### 2) Install
Use your virtualenv:

```bash
pip install -r requirements.txt
```

### 3) Migrate

```bash
python manage.py migrate
```

## Run (3 processes)

### Terminal 1 (API)

```bash
python manage.py runserver 0.0.0.0:8001
```

### Terminal 2 (Celery worker)

```bash
celery -A config.celery_app worker -l info
```

### Terminal 3 (Celery beat)

```bash
celery -A config.celery_app beat -l info
```

## Docs
- See `backend/docs/ARCHITECTURE.md`
- See `backend/docs/RULES.md`