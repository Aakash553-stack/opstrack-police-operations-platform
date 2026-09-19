# OpsTrack — Police Operations Intelligence & Management Platform

> **Fictional portfolio project.** OpsTrack is a synthetic-data
> demonstration of a full-stack internal operations system. It does not
> represent any real police department, officer, or incident. Built to
> showcase relational schema design, migration discipline, a typed API
> layer, and a modern frontend end-to-end.

**Stack:** React + TypeScript + Vite + Tailwind CSS (frontend) · FastAPI +
SQLAlchemy 2.0 + Alembic (backend) · PostgreSQL 16 (database).

## Status

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Requirements & architecture | ✅ Done |
| 2 | Database design (schema, ER diagram, normalization, constraint tests) | ✅ Done |
| 3 | Alembic migrations | ✅ Done |
| 4 | FastAPI backend | ✅ Done |
| 5 | Auth & authorization | ⬜ Not started |
| 6 | Backend test suite | ⬜ Not started |
| 7 | Frontend scaffold | ⬜ Not started |
| 8 | Frontend feature screens | ⬜ Not started |
| 9 | CI/CD | ⬜ Not started |
| 10 | Polish & seed data | ⬜ Not started |

See [`docs/01-requirements-and-architecture.md`](docs/01-requirements-and-architecture.md)
for the full roadmap and architecture.

## What's here so far (Phases 1–4)

- [`docs/01-requirements-and-architecture.md`](docs/01-requirements-and-architecture.md)
  — MVP/optional scope, architecture diagram, repo layout, 10-phase roadmap.
- [`docs/er-diagram.md`](docs/er-diagram.md) — Mermaid ER diagram of all 13
  tables.
- [`docs/normalization.md`](docs/normalization.md) — functional-dependency
  analysis per table and documented denormalization decisions.
- [`database/schema.sql`](database/schema.sql) — hand-authored 3NF
  PostgreSQL 16 schema: 13 tables, 8 ENUM types, CHECK/UNIQUE constraints,
  partial indexes, an `updated_at` trigger.
- [`database/tests/constraint_tests.sql`](database/tests/constraint_tests.sql)
  — 10 constraint-testing scenarios (duplicate badges, bad FKs, invalid
  date ranges, duplicate rosters, concurrent open assignments, no-op
  promotions, malformed badge formats, restricted/cascading/set-null
  deletes), verified against a live PostgreSQL 16 instance.
- `backend/app/models/` — SQLAlchemy 2.0 ORM models mirroring
  `database/schema.sql` exactly.
- `backend/alembic/` — Alembic migration environment. The initial
  migration reproduces `schema.sql` byte-for-byte (verified with a
  `pg_dump --schema-only` diff), and both its `upgrade`/`downgrade` cycle
  and the 10 constraint-test scenarios were re-run against the
  Alembic-built database to confirm equivalence.
- `backend/app/` — a running FastAPI app: Pydantic v2 schemas, a generic
  CRUD layer, and REST routers for all 13 resources under `/api/v1`
  (`/health` for liveness). Every DB-level integrity rule (uniqueness, FK,
  CHECK, partial-unique) is exercised end-to-end through the live API —
  duplicate badges, bad FKs, restricted deletes, and the one-open-
  assignment-per-officer rule all correctly surface as `409 Conflict`,
  while client-side format errors (e.g. a malformed badge number) are
  rejected as `422` before ever reaching the database. User passwords are
  bcrypt-hashed server-side and never echoed back.
- `backend/tests/` — a pytest smoke suite (`TestClient` + a real Postgres
  test database, each test wrapped in a rolled-back savepoint) covering
  the health check and the create/duplicate/restrict/update/delete flow
  above.

## Local setup

### Database only (schema verification)

```bash
createdb opstrack
psql -d opstrack -f database/schema.sql
psql -d opstrack -f database/tests/constraint_tests.sql   # expect 10x RESULT: PASS
```

### Backend (Alembic-managed database)

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp ../.env.example ../.env   # edit DATABASE_URL as needed
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload   # http://localhost:8000/docs
```

Run the backend test suite (needs a separate `opstrack_test` database):

```bash
createdb opstrack_test
cd backend
DATABASE_URL=postgresql+psycopg://opstrack:<password>@localhost:5432/opstrack_test \
  .venv/bin/pytest
```

### Full stack (once later phases land)

```bash
cp .env.example .env
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Database: localhost:5432

## Repository layout

See [`docs/01-requirements-and-architecture.md`](docs/01-requirements-and-architecture.md#4-repository-layout)
for the annotated tree.

## License

MIT — see [`LICENSE`](LICENSE).
