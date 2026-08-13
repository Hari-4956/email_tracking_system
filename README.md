# E STAR Email Tracking System

Email **open-tracking**, recipient/campaign APIs, analytics, and a read-only React admin dashboard.

Email **sending** is handled externally by an existing **n8n** workflow (Schedule Trigger → Google Sheets → IF → Gmail). FastAPI does **not** send email.

Tracked opens are best-effort. Treat analytics as **tracked opens**, not guaranteed human opens.

---

## Architecture

```text
n8n (Schedule → Google Sheets → IF → Gmail)
        ↓  HTML email with tracking pixel
Recipient opens email
        ↓
GET {BASE_URL}/track/open/{tracking_token}
        ↓
FastAPI + SQLAlchemy
        ↓
PostgreSQL (campaigns / recipients / email_events)
        ↓
React dashboard (read-only GET APIs)
```

**Do not modify the existing n8n workflow.** It is outside this repository’s deploy scope.

---

## Technology stack

- Python, FastAPI, Uvicorn, SQLAlchemy, PostgreSQL, Pydantic
- React + Vite + TypeScript + Recharts
- pandas / openpyxl (Excel import utilities only)

---

## Project structure

```text
email_tracking_system/
├── backend/                 # FastAPI API + tracking pixel
├── frontend/                # React admin dashboard
├── sender/                  # Excel → PostgreSQL import (not SMTP)
├── database/                # schema/index documentation SQL
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## Environment variables

Copy `.env.example` → `.env` (never commit `.env`).

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL SQLAlchemy URL |
| `BASE_URL` | Public origin for tracking links (`{BASE_URL}/track/open/{token}`) |
| `ENVIRONMENT` | `development` \| `testing` \| `production` |
| `CORS_ORIGINS` | Optional comma-separated frontend origins (empty = CORS off) |
| `DB_POOL_SIZE` | SQLAlchemy pool size (default 5) |
| `DB_MAX_OVERFLOW` | Pool overflow (default 10) |
| `DB_POOL_RECYCLE` | Seconds before recycling connections (default 1800) |
| `LOG_LEVEL` | `INFO` recommended; avoid noisy DEBUG in production |

Frontend (`frontend/.env`):

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | Empty in local dev (Vite proxy). Production: deployed API origin |

**Tracking URL format (do not change):**

```text
{BASE_URL}/track/open/{tracking_token}
```

Ngrok HTTPS URLs are fine for development only. Production should use a real domain.

---

## Backend setup (development)

```bash
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
```

Useful URLs:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health → `{"status":"healthy"}`
- http://127.0.0.1:8000/docs

`backend/create_table.py` is a **dev/setup utility only**. Do not use `create_all` as a production migration system.

---

## React setup (development)

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

Vite proxies `/api`, `/health`, and `/track` to FastAPI on port 8000.

### Production frontend build

```bash
cd frontend
npm install
npm run build
```

Serve `frontend/dist/` behind your web server / CDN.

Set:

```env
VITE_API_BASE_URL=https://api.your-domain.com
```

before building (or inject at build time). Do **not** rely on the Vite proxy in production.

If the dashboard is hosted on a different origin than the API, set backend:

```env
CORS_ORIGINS=https://dashboard.your-domain.com
```

Do **not** use `CORS_ORIGINS=*` in production unless you fully accept the risk.

---

## API overview

### Core

| Method | Path |
|--------|------|
| GET | `/` |
| GET | `/health` |
| GET | `/docs` |

### Tracking (public — no auth)

| Method | Path |
|--------|------|
| GET | `/track/open/{tracking_token}` |

Returns a 1×1 GIF, updates open fields, inserts `EmailEvent`.

### Recipients / campaigns / analytics

See `/docs`. Recipient list supports:

`search`, `status`, `opened`, `campaign_id`, `skip`, `limit` (max 500).

The React dashboard is **read-only** (GET only).

---

## Testing

```bash
.\venv\Scripts\pytest.exe -q
cd frontend
npm run build
```

---

## Deployment considerations

1. Set `ENVIRONMENT=production`.
2. Set `DATABASE_URL` via secret store / host env (not git).
3. Set `BASE_URL` to the public HTTPS origin that serves `/track/open/...`.
4. Run uvicorn (or gunicorn+uvicorn workers) behind a reverse proxy (nginx/Caddy/cloud LB).
5. Build frontend with production `VITE_API_BASE_URL`.
6. Keep `/track/open/{tracking_token}` publicly reachable — already-sent emails depend on it.
7. Do **not** change tracking URL paths or regenerate `tracking_token` values.
8. Do **not** restore the 7,304 removed empty-name recipients.
9. Do **not** modify the n8n → Gmail sending workflow as part of deploy.
10. Prefer documented `CREATE INDEX IF NOT EXISTS` from `database/indexes.sql` only after review; never DROP/TRUNCATE live data.

Example API process (Windows / Linux adapt as needed):

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## Security notes

- `.env` is gitignored; never commit credentials.
- API errors return safe messages (no stack traces / no DB passwords).
- Successful tracking hits are not logged at INFO (high volume).
- Tracking pixel remains unauthenticated by design.
- React never receives `DATABASE_URL` or PostgreSQL credentials.

---

## Data safety

Current verified campaign population (as of Phase 7 prep):

- Campaign 1: **E STAR Independence Day 2026**
- Recipients: **71,627** (not 78,931)
- Removed empty-name rows: **7,304** — do not restore

Preserve existing `tracking_token` values and `email_events` history.

---

## License / ownership

Internal E STAR project tooling.
