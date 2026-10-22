# 5e Digital Character Sheet

React (TS) + Vite, FastAPI, PostgreSQL.

## Run
```
cp .env.example .env
docker compose up -d                                  # Postgres
cd backend && uv run uvicorn app.main:app --reload    # API on :8000
cd frontend && npm install && npm run dev             # UI on :5173 (proxies /api)
```

## Character Model Overview

The goal is to create an extensible database of Dungeons & Dragons 5.5e character components, such as Classes, Species, Feats, Spells, etc. that are presented to the user an organizable digital "character sheet".

All bookkeeping is handled by the application, so that users don't need to worry about handling items such as calculating ability score modifier, skill-check bonuses, attack bonus, etc.

### Character Component Models

- CharacterClass
- Subclass
- Feat
- Spell

