-- =====================================================================
-- OpsTrack — Police Operations Intelligence & Management Platform
-- PostgreSQL 16 schema (3NF)
--
-- IMPORTANT: This is a fictional portfolio project. Every table, column,
-- and value in this schema describes SYNTHETIC data only. No real police
-- records, officers, or operations are represented anywhere in this
-- repository.
--
-- Design notes:
--   * 13 base tables, 8 ENUM types.
--   * Status/type columns that are expected to evolve over the project's
--     life (operation status, incident type, training type, etc.) are
--     modeled as TEXT + CHECK (value IN (...)) rather than ENUM, so new
--     values don't require ALTER TYPE ... ADD VALUE (which cannot run
--     inside a transaction in older PG and cannot be removed at all).
--     Columns that are genuinely fixed, small, and rarely-if-ever
--     extended (gender, officer status, user role, unit type, assignment
--     type, incident severity, shift) use native ENUM types for tighter
--     storage and self-documenting DDL.
--   * officers.rank_id is the single source of truth for an officer's
--     CURRENT rank. `promotions` is an append-only audit trail of rank
--     changes over time; it does not need to be joined to know an
--     officer's current rank, avoiding a derived/denormalized column.
--   * unit_assignments enforces "at most one OPEN assignment per officer"
--     via a partial unique index on (officer_id) WHERE end_date IS NULL,
--     rather than an application-level check, so it holds even under
--     concurrent writes.
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- Extensions
-- ---------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS citext;

-- ---------------------------------------------------------------------
-- ENUM types (8)
-- ---------------------------------------------------------------------
CREATE TYPE gender_enum            AS ENUM ('male', 'female', 'other');
CREATE TYPE officer_status_enum    AS ENUM ('active', 'on_leave', 'suspended', 'retired', 'terminated');
CREATE TYPE user_role_enum         AS ENUM ('admin', 'supervisor', 'officer', 'viewer');
CREATE TYPE unit_type_enum         AS ENUM ('headquarters', 'division', 'precinct', 'special_unit');
CREATE TYPE assignment_type_enum   AS ENUM ('permanent', 'temporary', 'detached');
CREATE TYPE operation_type_enum    AS ENUM ('raid', 'patrol_sweep', 'checkpoint', 'investigation', 'surveillance', 'crowd_control');
CREATE TYPE incident_severity_enum AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE shift_enum             AS ENUM ('morning', 'evening', 'night');

-- ---------------------------------------------------------------------
-- updated_at trigger function (shared by every table with that column)
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 1. ranks — rank hierarchy (Constable .. Inspector General)
-- =====================================================================
CREATE TABLE ranks (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    level       SMALLINT NOT NULL,      -- 1 = lowest rank, higher = senior
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_ranks_name UNIQUE (name),
    CONSTRAINT uq_ranks_level UNIQUE (level),
    CONSTRAINT ck_ranks_level_positive CHECK (level > 0)
);

-- =====================================================================
-- 2. units — organizational units (self-referential hierarchy)
-- =====================================================================
CREATE TABLE units (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    unit_type       unit_type_enum NOT NULL,
    parent_unit_id  INTEGER REFERENCES units(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_units_name UNIQUE (name),
    CONSTRAINT ck_units_not_own_parent CHECK (parent_unit_id IS DISTINCT FROM id)
);

CREATE TRIGGER trg_units_updated_at
    BEFORE UPDATE ON units
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 3. officers — sworn personnel
-- =====================================================================
CREATE TABLE officers (
    id                SERIAL PRIMARY KEY,
    badge_number      VARCHAR(15) NOT NULL,
    first_name        VARCHAR(60) NOT NULL,
    last_name         VARCHAR(60) NOT NULL,
    gender            gender_enum NOT NULL,
    date_of_birth     DATE NOT NULL,
    date_joined       DATE NOT NULL,
    rank_id           INTEGER NOT NULL REFERENCES ranks(id) ON DELETE RESTRICT,
    current_unit_id   INTEGER REFERENCES units(id) ON DELETE SET NULL,
    status            officer_status_enum NOT NULL DEFAULT 'active',
    contact_phone     VARCHAR(20),
    contact_email     CITEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_officers_badge_number UNIQUE (badge_number),
    CONSTRAINT uq_officers_contact_email UNIQUE (contact_email),
    CONSTRAINT ck_officers_badge_format CHECK (badge_number ~ '^[A-Z]{2,4}-[0-9]{4,6}$'),
    CONSTRAINT ck_officers_joined_after_birth CHECK (date_joined > date_of_birth),
    CONSTRAINT ck_officers_min_age CHECK (date_joined >= date_of_birth + INTERVAL '18 years')
);

CREATE INDEX idx_officers_rank_id ON officers(rank_id);
CREATE INDEX idx_officers_current_unit_id ON officers(current_unit_id);
-- Fast lookup of active roster per unit (the overwhelmingly common query)
CREATE INDEX idx_officers_active_unit ON officers(current_unit_id) WHERE status = 'active';

CREATE TRIGGER trg_officers_updated_at
    BEFORE UPDATE ON officers
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 4. users — application login accounts (at most one per officer)
-- =====================================================================
CREATE TABLE users (
    id             SERIAL PRIMARY KEY,
    officer_id     INTEGER REFERENCES officers(id) ON DELETE CASCADE,
    username       CITEXT NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    role           user_role_enum NOT NULL DEFAULT 'officer',
    is_active      BOOLEAN NOT NULL DEFAULT true,
    last_login_at  TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_users_username UNIQUE (username)
);

-- One login account per officer at most
CREATE UNIQUE INDEX uq_users_officer_id ON users(officer_id) WHERE officer_id IS NOT NULL;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 5. promotions — append-only rank-change history
-- =====================================================================
CREATE TABLE promotions (
    id               SERIAL PRIMARY KEY,
    officer_id       INTEGER NOT NULL REFERENCES officers(id) ON DELETE RESTRICT,
    from_rank_id     INTEGER REFERENCES ranks(id) ON DELETE RESTRICT,
    to_rank_id       INTEGER NOT NULL REFERENCES ranks(id) ON DELETE RESTRICT,
    promotion_date   DATE NOT NULL,
    approved_by_id   INTEGER REFERENCES officers(id) ON DELETE SET NULL,
    notes            TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_promotions_rank_change CHECK (from_rank_id IS DISTINCT FROM to_rank_id)
);

CREATE INDEX idx_promotions_officer_id ON promotions(officer_id);
CREATE INDEX idx_promotions_promotion_date ON promotions(promotion_date);

-- =====================================================================
-- 6. unit_assignments — officer <-> unit assignment history
-- =====================================================================
CREATE TABLE unit_assignments (
    id               SERIAL PRIMARY KEY,
    officer_id       INTEGER NOT NULL REFERENCES officers(id) ON DELETE CASCADE,
    unit_id          INTEGER NOT NULL REFERENCES units(id) ON DELETE RESTRICT,
    assignment_type  assignment_type_enum NOT NULL DEFAULT 'permanent',
    start_date       DATE NOT NULL,
    end_date         DATE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_unit_assignments_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_unit_assignments_officer_id ON unit_assignments(officer_id);
CREATE INDEX idx_unit_assignments_unit_id ON unit_assignments(unit_id);
-- At most one OPEN (end_date IS NULL) assignment per officer at any time
CREATE UNIQUE INDEX uq_unit_assignments_open_officer
    ON unit_assignments(officer_id) WHERE end_date IS NULL;

CREATE TRIGGER trg_unit_assignments_updated_at
    BEFORE UPDATE ON unit_assignments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 7. operations — planned/active law-enforcement operations
-- =====================================================================
CREATE TABLE operations (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(150) NOT NULL,
    operation_type operation_type_enum NOT NULL,
    status         TEXT NOT NULL DEFAULT 'planned',
    lead_unit_id   INTEGER NOT NULL REFERENCES units(id) ON DELETE RESTRICT,
    start_date     DATE NOT NULL,
    end_date       DATE,
    description    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_operations_status CHECK (status IN ('planned', 'active', 'completed', 'cancelled')),
    CONSTRAINT ck_operations_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_operations_lead_unit_id ON operations(lead_unit_id);
CREATE INDEX idx_operations_active ON operations(status) WHERE status IN ('planned', 'active');

CREATE TRIGGER trg_operations_updated_at
    BEFORE UPDATE ON operations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 8. operation_participants — officers assigned to an operation
-- =====================================================================
CREATE TABLE operation_participants (
    id                 SERIAL PRIMARY KEY,
    operation_id       INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
    officer_id         INTEGER NOT NULL REFERENCES officers(id) ON DELETE RESTRICT,
    role_in_operation  TEXT NOT NULL DEFAULT 'participant',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_operation_participants_role CHECK (role_in_operation IN ('lead', 'participant', 'support')),
    CONSTRAINT uq_operation_participants UNIQUE (operation_id, officer_id)
);

CREATE INDEX idx_operation_participants_officer_id ON operation_participants(officer_id);

-- =====================================================================
-- 9. patrols — scheduled/completed patrol shifts
-- =====================================================================
CREATE TABLE patrols (
    id               SERIAL PRIMARY KEY,
    unit_id          INTEGER NOT NULL REFERENCES units(id) ON DELETE RESTRICT,
    officer_id       INTEGER NOT NULL REFERENCES officers(id) ON DELETE RESTRICT,
    patrol_date      DATE NOT NULL,
    shift            shift_enum NOT NULL,
    start_time       TIME NOT NULL,
    end_time         TIME NOT NULL,
    vehicle_code     VARCHAR(20),
    area_description VARCHAR(200),
    status           TEXT NOT NULL DEFAULT 'scheduled',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_patrols_status CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT ck_patrols_times CHECK (end_time > start_time)
);

CREATE INDEX idx_patrols_officer_id ON patrols(officer_id);
CREATE INDEX idx_patrols_unit_id ON patrols(unit_id);
CREATE INDEX idx_patrols_patrol_date ON patrols(patrol_date);

CREATE TRIGGER trg_patrols_updated_at
    BEFORE UPDATE ON patrols
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 10. incidents — reported incidents/cases
-- =====================================================================
CREATE TABLE incidents (
    id                    SERIAL PRIMARY KEY,
    incident_number       VARCHAR(20) NOT NULL,
    incident_type         TEXT NOT NULL,
    severity              incident_severity_enum NOT NULL DEFAULT 'low',
    status                TEXT NOT NULL DEFAULT 'reported',
    reported_date         TIMESTAMPTZ NOT NULL DEFAULT now(),
    location_description  VARCHAR(200) NOT NULL,
    reporting_officer_id  INTEGER NOT NULL REFERENCES officers(id) ON DELETE RESTRICT,
    assigned_unit_id      INTEGER REFERENCES units(id) ON DELETE SET NULL,
    operation_id          INTEGER REFERENCES operations(id) ON DELETE SET NULL,
    description           TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_incidents_incident_number UNIQUE (incident_number),
    CONSTRAINT ck_incidents_type CHECK (incident_type IN
        ('theft', 'assault', 'traffic', 'homicide', 'fraud', 'public_disturbance', 'other')),
    CONSTRAINT ck_incidents_status CHECK (status IN
        ('reported', 'under_investigation', 'resolved', 'closed'))
);

CREATE INDEX idx_incidents_assigned_unit_id ON incidents(assigned_unit_id);
CREATE INDEX idx_incidents_reporting_officer_id ON incidents(reporting_officer_id);
CREATE INDEX idx_incidents_operation_id ON incidents(operation_id);
CREATE INDEX idx_incidents_open ON incidents(status) WHERE status IN ('reported', 'under_investigation');

CREATE TRIGGER trg_incidents_updated_at
    BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 11. training_sessions — scheduled training courses
-- =====================================================================
CREATE TABLE training_sessions (
    id               SERIAL PRIMARY KEY,
    title            VARCHAR(150) NOT NULL,
    training_type    TEXT NOT NULL,
    instructor_name  VARCHAR(100) NOT NULL,
    location         VARCHAR(150) NOT NULL,
    start_date       DATE NOT NULL,
    end_date         DATE NOT NULL,
    capacity         SMALLINT NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_training_sessions_type CHECK (training_type IN
        ('firearms', 'legal', 'physical', 'cyber', 'first_aid', 'ethics')),
    CONSTRAINT ck_training_sessions_dates CHECK (end_date >= start_date),
    CONSTRAINT ck_training_sessions_capacity CHECK (capacity > 0)
);

CREATE INDEX idx_training_sessions_start_date ON training_sessions(start_date);

CREATE TRIGGER trg_training_sessions_updated_at
    BEFORE UPDATE ON training_sessions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- 12. training_attendance — officer attendance/results per session
-- =====================================================================
CREATE TABLE training_attendance (
    id                    SERIAL PRIMARY KEY,
    training_session_id   INTEGER NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
    officer_id            INTEGER NOT NULL REFERENCES officers(id) ON DELETE CASCADE,
    attendance_status     TEXT NOT NULL DEFAULT 'registered',
    score                 NUMERIC(5, 2),
    certificate_issued    BOOLEAN NOT NULL DEFAULT false,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_training_attendance_status CHECK (attendance_status IN
        ('registered', 'attended', 'absent', 'excused')),
    CONSTRAINT ck_training_attendance_score CHECK (score IS NULL OR (score >= 0 AND score <= 100)),
    CONSTRAINT uq_training_attendance UNIQUE (training_session_id, officer_id)
);

CREATE INDEX idx_training_attendance_officer_id ON training_attendance(officer_id);

-- =====================================================================
-- 13. audit_logs — application-level audit trail
-- =====================================================================
CREATE TABLE audit_logs (
    id           BIGSERIAL PRIMARY KEY,
    user_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action       TEXT NOT NULL,
    table_name   VARCHAR(100) NOT NULL,
    record_id    INTEGER,
    old_values   JSONB,
    new_values   JSONB,
    ip_address   INET,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_audit_logs_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

COMMIT;
