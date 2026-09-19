# OpsTrack — Requirements & Architecture

> **Disclaimer:** OpsTrack is a fictional portfolio project. All entities,
> data, and scenarios are synthetic. It does not represent any real police
> department, and no real law-enforcement data is used anywhere in this
> repository.

## 1. Purpose

OpsTrack is a Police Operations Intelligence & Management Platform that
tracks officers, organizational units, operations, patrols, incidents, and
training — the kind of internal system a mid-size department might use to
coordinate personnel and log activity. It's built as a full-stack portfolio
project demonstrating relational schema design, migration discipline, a
typed API layer, and a modern frontend.

## 2. Scope

### 2.1 MVP scope

- **Personnel management** — officers, ranks, rank promotions, organizational
  units, and unit assignment history.
- **Operations management** — planning and tracking operations (raids,
  checkpoints, investigations, surveillance, crowd control) and which
  officers participate in each.
- **Patrol scheduling** — shift-based patrol assignments per unit/officer.
- **Incident tracking** — logging reported incidents, severity, status, and
  the unit/officer/operation they're tied to.
- **Training records** — scheduled training sessions and per-officer
  attendance/certification.
- **Authentication & authorization** — login accounts tied to officers with
  role-based access (admin / supervisor / officer / viewer).
- **Audit logging** — an append-only trail of who changed what.

### 2.2 Optional / stretch scope

- Geospatial mapping of incidents/patrols (PostGIS).
- Real-time dashboards (WebSocket-driven operational status).
- File attachments (evidence photos, reports) via object storage.
- Advanced reporting/analytics (officer workload, incident heatmaps).
- Notification system (shift reminders, operation briefings).
- Multi-department/tenant support.

Optional scope is explicitly **not** part of the phase roadmap below unless
called out; it exists to show room for growth.

## 3. Architecture overview

```
┌─────────────────────┐        HTTPS/JSON         ┌──────────────────────────┐
│   Frontend (SPA)     │ ────────────────────────▶ │   Backend (REST API)     │
│  React + TypeScript  │ ◀──────────────────────── │  FastAPI + SQLAlchemy    │
│  Vite + Tailwind CSS │                            │  2.0 + Pydantic v2       │
└──────────────────────┘                            └────────────┬─────────────┘
                                                                  │ asyncpg/psycopg
                                                                  ▼
                                                     ┌──────────────────────────┐
                                                     │   PostgreSQL 16          │
                                                     │   (schema.sql / Alembic) │
                                                     └──────────────────────────┘
```

- **Frontend**: React 18 + TypeScript, built with Vite, styled with
  Tailwind CSS. Talks to the backend exclusively over a versioned REST API
  (`/api/v1/...`).
- **Backend**: FastAPI (async), SQLAlchemy 2.0 ORM (typed declarative
  models), Pydantic v2 schemas for request/response validation, Alembic for
  schema migrations. JWT-based auth.
- **Database**: PostgreSQL 16, 3NF relational schema (see
  `database/schema.sql`), owned by Alembic migrations from Phase 3 onward.
- **Containerization**: `docker-compose.yml` wires up `db`, `backend`, and
  `frontend` services for local development.
- **CI**: GitHub Actions (`.github/workflows/`) runs backend tests +
  migrations against a Postgres service container, and frontend
  lint/build, on every push/PR.

## 4. Repository layout

```
opstrack-police-operations-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI routers
│   │   ├── core/            # config, security, dependencies
│   │   ├── crud/            # DB access functions
│   │   ├── db/              # session/engine setup
│   │   ├── models/          # SQLAlchemy 2.0 ORM models
│   │   └── schemas/         # Pydantic request/response models
│   ├── alembic/              # migration environment + versions/
│   ├── tests/                # backend test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # typed API client
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── pages/
│   │   └── types/
│   └── package.json
├── database/
│   ├── schema.sql             # hand-authored reference schema (3NF)
│   └── tests/
│       └── constraint_tests.sql
├── docs/
│   ├── 01-requirements-and-architecture.md
│   ├── er-diagram.md
│   └── normalization.md
├── tests/
│   └── integration/           # cross-stack integration tests
├── .github/workflows/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── LICENSE
```

## 5. Roadmap (10 phases)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Requirements & architecture (this document) | ✅ Done |
| 2 | Database design: `schema.sql`, ER diagram, normalization analysis, constraint testing | ✅ Done |
| 3 | Alembic migrations reproducing `schema.sql` exactly | ✅ Done |
| 4 | FastAPI backend: models, schemas, CRUD, core routers | ✅ Done |
| 5 | Authentication & authorization (JWT, role-based access) | ⬜ Not started |
| 6 | Backend test suite (unit + integration against a real DB) | ⬜ Not started |
| 7 | React frontend scaffold: routing, API client, auth flow | ⬜ Not started |
| 8 | Frontend feature screens (roster, operations, patrols, incidents, training) | ⬜ Not started |
| 9 | CI/CD: GitHub Actions for backend + frontend, Docker Compose for local dev | ⬜ Not started |
| 10 | Polish: seed data, docs pass, deployment notes | ⬜ Not started |

## 6. Key technical decisions

- **PostgreSQL enums vs. CHECK constraints**: fixed, rarely-changing
  domains (gender, officer status, user role, unit type, assignment type,
  incident severity, shift) are native `ENUM` types. Domains expected to
  evolve (operation/incident/training status and type values) are
  `TEXT + CHECK` so adding a value is a plain migration, not an
  `ALTER TYPE`.
- **Migrations own the schema from Phase 3 onward**: `database/schema.sql`
  is the authoritative, hand-verified starting point; Alembic's initial
  migration is generated to reproduce it exactly and is diffed against it
  as a verification step, not written independently.
- **Soft status over hard deletes**: officers, operations, patrols, and
  incidents use status columns rather than row deletion, preserving
  history for audit purposes.
