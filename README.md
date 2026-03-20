# Backend (Django + DRF)

## What this does
- Fetches **real NIFTY 50** data from NSE.
- Saves snapshots into Postgres during market hours.
- Serves a polling API for the frontend:
  - `GET /api/nifty/latest/`
  - `GET /api/nifty/series/?range=1D|1M|3M|6M|1Y`
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

## Run (1 process)

### Terminal 1 (API)

```bash
python manage.py runserver 0.0.0.0:8001
```

Note: Nifty fetching runs automatically inside the Django web process
(see `dashboard_backend.nifty.scheduler`).


## Docs
- See `backend/docs/ARCHITECTURE.md`
- See `backend/docs/RULES.md`