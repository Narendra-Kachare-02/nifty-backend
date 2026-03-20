# Deployment Guide

This guide covers deploying the Nifty50 application with:
- **Frontend**: Vercel
- **Backend**: Render (with PostgreSQL and Redis)

## Architecture

```
┌─────────────┐         ┌─────────────────────────────────────────┐
│   Vercel    │         │              Render                     │
│  (Frontend) │ ──────► │  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│   React +   │   API   │  │ Django  │  │ Async   │  │ Fetch   │ │
│    Vite     │ Requests│  │   API   │  │ Worker  │  │         │ │
└─────────────┘         │  └────┬────┘  └────┬────┘  └────┬────┘ │
                        │       │            │            │      │
                        │  ┌────▼────────────▼────────────▼────┐ │
                        │  │         PostgreSQL + Redis        │ │
                        │  └───────────────────────────────────┘ │
                        └─────────────────────────────────────────┘
```

## Frontend Deployment (Vercel)

### Setup Steps

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: `bun run build`
   - **Output Directory**: `dist`

### Environment Variables

Set these in Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL (from Render) | `https://nifty-api.onrender.com/` |
| `VITE_NIFTY_POLL_INTERVAL_MS` | Polling interval in ms | `5000` |
| `VITE_NIFTY_OPTION_LOT_SIZE` | Option lot size | `65` |

### Post-Deployment

After backend is deployed, update `VITE_API_BASE_URL` with the actual Render URL.

---

## Backend Deployment (Render)

### Setup Steps (Using Blueprint)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Select the repository and set root directory to `backend`
5. Render will read `render.yaml` and create all services automatically

### Services Created by Blueprint

| Service | Type | Description |
|---------|------|-------------|
| `nifty-postgres` | PostgreSQL | Database |
| `nifty-redis` | Redis | Cache |
| `nifty-api` | Web Service | Django REST API |

### Environment Variables

These are automatically configured by the Blueprint, but you need to manually add:

#### Required (Manual Setup in Render Dashboard)

| Variable | Service(s) | Description |
|----------|-----------|-------------|
| `FRONTEND_URL` | nifty-api | Your Vercel frontend URL (e.g., `https://your-app.vercel.app`) |
| `JWT_SECRET` | nifty-api | JWT signing key (generate a secure random string) |

#### Optional (Add if needed)

| Variable | Service(s) | Description |
|----------|-----------|-------------|
| `TWILIO_ACCOUNT_SID` | nifty-api | Twilio account SID for OTP |
| `TWILIO_AUTH_TOKEN` | nifty-api | Twilio auth token |
| `TWILIO_VERIFY_SERVICE_SID` | nifty-api | Twilio verify service SID |
| `EXTRA_CORS_ORIGINS` | nifty-api | Additional CORS origins (comma-separated) |
| `GOOGLE_APPLICATION_CREDENTIALS` | nifty-api | Path to Firebase credentials JSON |

#### Auto-configured by Blueprint

These are automatically set by Render's Blueprint:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (auto-generated) |
| `DEBUG` | Set to `False` |
| `DJANGO_ALLOWED_HOSTS` | Set to `.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `CELERY_BROKER_URL` | Celery broker URL (Redis) (optional) |
| `CELERY_RESULT_BACKEND` | Celery result backend (Redis) (optional) |

---

## Manual Deployment (Without Blueprint)

If you prefer manual setup:

### 1. Create PostgreSQL Database

- Go to Render Dashboard → New → PostgreSQL
- Name: `nifty-postgres`
- Database: `nifty_management`
- Copy the **Internal Database URL**

### 2. Create Redis Instance

- Go to Render Dashboard → New → Redis
- Name: `nifty-redis`
- Copy the **Internal Redis URL**

### 3. Create Web Service (Django API)

- Go to Render Dashboard → New → Web Service
- Connect repository, set root to `backend`
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
- Add environment variables (see above)

### 4. Create Async Fetch Worker

- Go to Render Dashboard → New → Background Worker
- **Build Command**: `pip install -r requirements.txt`
 - No extra worker service is required; the schedule runs inside `nifty-api` (web) via `dashboard_backend.nifty.scheduler`.

---

## Post-Deployment Checklist

- [ ] Backend deployed and accessible at `https://nifty-api.onrender.com`
- [ ] Database migrations completed successfully
- [ ] Frontend deployed and accessible at Vercel URL
- [ ] Updated `VITE_API_BASE_URL` in Vercel with Render backend URL
- [ ] Updated `FRONTEND_URL` in Render with Vercel frontend URL
- [ ] Tested API connectivity from frontend
- [ ] Nifty scheduler is running (check `nifty-api` logs)
- [ ] (Optional) Added custom domains in both platforms

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Check `FRONTEND_URL` is set correctly in Render
2. Add additional origins to `EXTRA_CORS_ORIGINS` if needed
3. Ensure URLs include protocol (`https://`)

### Database Connection Issues

1. Check `DATABASE_URL` is set
2. Verify PostgreSQL service is running in Render
3. Check logs for connection errors

### Static Files Not Loading

1. Ensure `collectstatic` ran during build
2. Check WhiteNoise middleware is enabled
3. Verify `STATIC_ROOT` directory exists

### Nifty Async Fetch Not Running

1. Check `nifty-api` logs for `Nifty schedule scheduler started` / tick messages
2. Verify `DATABASE_URL` is set and PostgreSQL is reachable
3. Ensure the web process is running (Redis/Celery are not required for Nifty fetching)
