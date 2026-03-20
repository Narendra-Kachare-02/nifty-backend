# Backend architecture (Nifty)

## Goal
- Fetch **real live** NIFTY 50 index + constituents from NSE.
- Persist snapshots in Postgres so **after market close** we keep serving the **last recorded** data.

## Data flow
1. **In-process scheduler** (`dashboard_backend.nifty.scheduler`) runs every minute and calls `dashboard_backend.nifty.tasks.fetchNifty` / `fetchOptionChain`.
2. Each async task checks market hours (`isMarketOpenNow`) to avoid NSE calls outside **09:15–15:15 IST** (Mon–Fri).
3. Task calls:
   - `services.fetchNifty.fetchNiftyPayload` (Index API: `getIndexData`)
   - `services.saveNiftySnapshot.saveNiftySnapshot` (DB write)
   - `services.fetchNiftyChart.fetchNiftyChartPayload` (Chart API: `getIndexChart`, default `1D`)
   - `services.saveNiftyChartSnapshot.saveNiftyChartSnapshot`
4. Option chain task calls:
   - `services.fetchOptionChainContractInfo.fetchOptionChainContractInfo`
   - `services.fetchOptionChain.fetchOptionChainPayload` (Option Chain v3)
   - `services.saveOptionChainSnapshot.saveOptionChainSnapshot`
5. APIs:
   - `GET /api/nifty/latest/`
   - `GET /api/nifty/series/?range=1D|1M|3M|6M|1Y`
   - `GET /api/nifty/option-chain/latest/?expiryDate=...`

## DRY + responsibilities
- **Views** (`views.py`): request/response only.
- **Services** (`services/`): one responsibility per file (fetch / save / read).
- **Config** (`config.py`): NSE URLs/headers, market hours, intervals.
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

