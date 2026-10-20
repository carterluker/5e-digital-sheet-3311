# 5e Digital Character Sheet

React (TS) + Vite, FastAPI, PostgreSQL.

## Run
```
cp .env.example .env
docker compose up -d                                  # Postgres
cd backend && uv run uvicorn app.main:app --reload    # API on :8000
cd frontend && npm install && npm run dev             # UI on :5173 (proxies /api)
```

## Backend API (demo)

Interactive docs at http://localhost:8000/docs. Tests (SQLite in-memory, no Postgres needed):
`cd backend && uv run pytest`

| Area | Endpoints |
|---|---|
| Auth (bearer token) | `POST /api/auth/register`, `/login`, `/logout`, `GET /me` |
| Characters | `GET/POST /api/characters`, `GET/PUT/DELETE /api/characters/{id}` |
| Autosave | `PUT /api/characters/{id}` with `{version, data, layout?}`; 409 on stale version |
| Backups | `GET/POST /{id}/backups`, `GET /{id}/backups/{bid}`, `POST /{id}/backups/{bid}/restore` |
| Rules | every character response includes `derived` stats and rule `issues`; `POST /api/characters/validate` is a stateless dry run |
| Bookkeeping | `POST /{id}/actions` — `damage`, `heal`, `temp_hp`, `death_save`, `add_item`, `remove_item`, `equip`, `currency`, `condition`, `use_resource`, `use_spell_slot`, `spend_hit_dice`, `short_rest`, `long_rest` |

Design notes:
- The sheet is a JSON document (`app/sheet.py`) in a JSON column; layout is stored beside it.
- Rule violations never block a save (autosave must not lose work); they come back as `issues`.
  Malformed data (wrong types, level 25) is rejected with 422.
- Autosave snapshots the *previous* state when the newest backup is older than `BACKUP_INTERVAL_SECONDS`
  (default 300), keeping the newest `MAX_BACKUPS_PER_CHARACTER` (20). Restoring first backs up the state it replaces.
- Tables are created on startup (no migrations in the demo). Passwords use scrypt; tokens are opaque and stored hashed.
- Not yet covered: multiclassing, feats/spell lists, warlock/subclass casters.
