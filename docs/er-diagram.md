# OpsTrack — Entity-Relationship Diagram

> Generated from `database/schema.sql`. All entities are synthetic
> (fictional portfolio project).

```mermaid
erDiagram
    RANKS ||--o{ OFFICERS : "holds"
    RANKS ||--o{ PROMOTIONS : "from_rank"
    RANKS ||--o{ PROMOTIONS : "to_rank"

    UNITS ||--o{ UNITS : "parent_unit"
    UNITS ||--o{ OFFICERS : "current_unit"
    UNITS ||--o{ UNIT_ASSIGNMENTS : "assigned_to"
    UNITS ||--o{ OPERATIONS : "leads"
    UNITS ||--o{ PATROLS : "runs"
    UNITS ||--o{ INCIDENTS : "assigned_to"

    OFFICERS ||--o| USERS : "has_login"
    OFFICERS ||--o{ PROMOTIONS : "promoted"
    OFFICERS ||--o{ PROMOTIONS : "approved_by"
    OFFICERS ||--o{ UNIT_ASSIGNMENTS : "assigned"
    OFFICERS ||--o{ OPERATION_PARTICIPANTS : "participates"
    OFFICERS ||--o{ PATROLS : "patrols"
    OFFICERS ||--o{ INCIDENTS : "reports"
    OFFICERS ||--o{ TRAINING_ATTENDANCE : "attends"

    USERS ||--o{ AUDIT_LOGS : "performs"

    OPERATIONS ||--o{ OPERATION_PARTICIPANTS : "includes"
    OPERATIONS ||--o{ INCIDENTS : "linked_to"

    TRAINING_SESSIONS ||--o{ TRAINING_ATTENDANCE : "has"

    RANKS {
        int id PK
        varchar name UK
        smallint level UK
        timestamptz created_at
    }

    UNITS {
        int id PK
        varchar name UK
        enum unit_type
        int parent_unit_id FK
        timestamptz created_at
        timestamptz updated_at
    }

    OFFICERS {
        int id PK
        varchar badge_number UK
        varchar first_name
        varchar last_name
        enum gender
        date date_of_birth
        date date_joined
        int rank_id FK
        int current_unit_id FK
        enum status
        citext contact_email UK
        varchar contact_phone
        timestamptz created_at
        timestamptz updated_at
    }

    USERS {
        int id PK
        int officer_id FK "UK, nullable"
        citext username UK
        varchar password_hash
        enum role
        bool is_active
        timestamptz last_login_at
        timestamptz created_at
        timestamptz updated_at
    }

    PROMOTIONS {
        int id PK
        int officer_id FK
        int from_rank_id FK
        int to_rank_id FK
        date promotion_date
        int approved_by_id FK
        text notes
        timestamptz created_at
    }

    UNIT_ASSIGNMENTS {
        int id PK
        int officer_id FK
        int unit_id FK
        enum assignment_type
        date start_date
        date end_date "nullable, partial-unique when NULL"
        timestamptz created_at
        timestamptz updated_at
    }

    OPERATIONS {
        int id PK
        varchar name
        enum operation_type
        text status "CHECK"
        int lead_unit_id FK
        date start_date
        date end_date
        text description
        timestamptz created_at
        timestamptz updated_at
    }

    OPERATION_PARTICIPANTS {
        int id PK
        int operation_id FK
        int officer_id FK
        text role_in_operation "CHECK"
        timestamptz created_at
    }

    PATROLS {
        int id PK
        int unit_id FK
        int officer_id FK
        date patrol_date
        enum shift
        time start_time
        time end_time
        varchar vehicle_code
        varchar area_description
        text status "CHECK"
        timestamptz created_at
        timestamptz updated_at
    }

    INCIDENTS {
        int id PK
        varchar incident_number UK
        text incident_type "CHECK"
        enum severity
        text status "CHECK"
        timestamptz reported_date
        varchar location_description
        int reporting_officer_id FK
        int assigned_unit_id FK
        int operation_id FK
        text description
        timestamptz created_at
        timestamptz updated_at
    }

    TRAINING_SESSIONS {
        int id PK
        varchar title
        text training_type "CHECK"
        varchar instructor_name
        varchar location
        date start_date
        date end_date
        smallint capacity
        timestamptz created_at
        timestamptz updated_at
    }

    TRAINING_ATTENDANCE {
        int id PK
        int training_session_id FK
        int officer_id FK
        text attendance_status "CHECK"
        numeric score
        bool certificate_issued
        timestamptz created_at
    }

    AUDIT_LOGS {
        bigint id PK
        int user_id FK "nullable"
        text action "CHECK"
        varchar table_name
        int record_id
        jsonb old_values
        jsonb new_values
        inet ip_address
        timestamptz created_at
    }
```

## Notable relationship rules (enforced at the DB level, not just app-level)

- `officers.badge_number` is unique and must match `^[A-Z]{2,4}-[0-9]{4,6}$`.
- `users.officer_id` is unique (partial index, `WHERE officer_id IS NOT NULL`)
  — at most one login account per officer.
- `unit_assignments` allows only one row per officer with `end_date IS NULL`
  (partial unique index) — an officer cannot have two open assignments.
- `operation_participants` is unique on `(operation_id, officer_id)`.
- `training_attendance` is unique on `(training_session_id, officer_id)`.
- `promotions.from_rank_id <> to_rank_id` — no no-op promotions.
- Deleting a `rank` or `unit` that is still referenced by `officers` is
  **restricted** (`ON DELETE RESTRICT`); deleting a `unit` referenced by
  `officers.current_unit_id` alone (not via FK restrict) is **not** the
  case — see schema for exact per-column delete behavior (mixed
  RESTRICT/SET NULL/CASCADE by relationship semantics).
