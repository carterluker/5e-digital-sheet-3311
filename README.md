# 5e Digital Character Sheet

React (TS) + Vite, FastAPI, PostgreSQL.

## Run
```
cp .env.example .env
docker compose up -d                                  # Postgres
cd backend && uv run uvicorn app.main:app --reload    # API on :8000
cd frontend && npm install && npm run dev             # UI on :5173 (proxies /api)
```