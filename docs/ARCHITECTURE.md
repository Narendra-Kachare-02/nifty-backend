# Backend architecture (Nifty)

## Goal
- Fetch **real live** NIFTY 50 index + constituents from NSE.
- Persist snapshots in Postgres so **after market close** we keep serving the **last recorded** data.

## Data flow
1. **Celery Beat** enqueues `nifty.fetchNifty` only during **09:15–15:30 IST** (Mon–Fri).
2. **Celery Worker** runs `dashboard_backend.nifty.tasks.fetchNifty`.
3. **Celery Beat** also enqueues `nifty.fetchOptionChain` only during **09:15–15:30 IST** (Mon–Fri).
4. **Celery Worker** runs `dashboard_backend.nifty.tasks.fetchOptionChain`.
3. Task calls:
   - `services.fetchNifty.fetchNiftyPayload` (NSE cookie warm-up + JSON fetch)
   - `services.saveNiftySnapshot.saveNiftySnapshot` (DB write)
4. Option chain task calls:
   - `services.fetchOptionChain.fetchOptionChainPayload`
   - `services.saveOptionChainSnapshot.saveOptionChainSnapshot`
5. APIs:
   - `GET /api/nifty/latest/`
   - `GET /api/nifty/series/?range=15M|30M|1H|1D`
   - `GET /api/nifty/option-chain/latest/?expiryDate=...`

## DRY + responsibilities
- **Views** (`views.py`): request/response only.
- **Services** (`services/`): one responsibility per file (fetch / save / read).
- **Constants** (`constants/`): NSE URLs/headers, market hours, intervals.
- **Utils** (`utils/`): pure helpers like market-hours checks.
- **Exceptions**: use custom exceptions when needed; response formatting is handled by `dashboard_backend.utils.rest_exception_handler.rest_exception_handler`.

## API response shape (stable)
`GET /api/nifty/latest/` returns:
- `captured_at`
- `name`
- `advance`
- `timestamp`
- `marketStatus`
- `metadata`
- `data`

Keys are kept **as-is** from NSE payload for simple mapping in frontend.

