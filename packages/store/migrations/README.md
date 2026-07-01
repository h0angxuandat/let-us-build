# Migrations (Alembic)

Async Alembic environment for `lub_store`. URL comes from `LUB_DATABASE_URL`.

```bash
# from repo root, with Postgres up (docker compose up -d)
uv run alembic -c packages/store/alembic.ini upgrade head
uv run alembic -c packages/store/alembic.ini revision --autogenerate -m "message"
```
