# OpsTrack — Normalization Analysis

This document walks through the functional dependencies (FDs) behind each
table in `database/schema.sql` and confirms the schema is in Third Normal
Form (3NF), then calls out the handful of deliberate denormalization-style
decisions and explains why each is safe.

Notation: `X → Y` means "X functionally determines Y" (given a value of X,
there's exactly one valid value of Y).

## 1. ranks

**Attributes:** id, name, level, created_at

**FDs:**
- `id → name, level, created_at`
- `name → id, level, created_at` (name is a candidate key, UNIQUE)
- `level → id, name, created_at` (level is a candidate key, UNIQUE)

No partial or transitive dependencies — every non-key attribute depends on
the whole (single-column) key. **3NF.**

## 2. units

**Attributes:** id, name, unit_type, parent_unit_id, created_at, updated_at

**FDs:**
- `id → name, unit_type, parent_unit_id, created_at, updated_at`
- `name → id, unit_type, parent_unit_id, ...` (name is UNIQUE)

`parent_unit_id` is a self-referential FK, not a derived attribute — no
transitive dependency introduced. **3NF.**

## 3. officers

**Attributes:** id, badge_number, first_name, last_name, gender,
date_of_birth, date_joined, rank_id, current_unit_id, status,
contact_phone, contact_email, created_at, updated_at

**FDs:**
- `id → all other attributes`
- `badge_number → all other attributes` (UNIQUE candidate key)
- `contact_email → id, ...` (UNIQUE)

`rank_id` and `current_unit_id` are FKs to `ranks`/`units`, not
transitively-derivable attributes (e.g., we do not store `rank_name` here —
that would be a transitive dependency `id → rank_id → rank_name` and a 3NF
violation). **3NF.**

**Rejected alternative:** storing the officer's rank *name* directly on
`officers` instead of `rank_id`. This would create a transitive dependency
(`officers.rank_id → ranks.name`) and risk the two going out of sync on a
rank rename. Rejected in favor of the FK.

## 4. users

**Attributes:** id, officer_id, username, password_hash, role, is_active,
last_login_at, created_at, updated_at

**FDs:**
- `id → all other attributes`
- `username → id, ...` (UNIQUE)
- `officer_id → id, ...` when not null (partial unique index enforces
  at most one user row per officer)

`officer_id` is nullable to allow non-sworn/admin accounts (e.g., a system
administrator) that aren't tied to an officer record. **3NF.**

## 5. promotions

**Attributes:** id, officer_id, from_rank_id, to_rank_id, promotion_date,
approved_by_id, notes, created_at

**FDs:**
- `id → all other attributes`

This is a pure history/log table — there is no natural composite key
(an officer can be promoted more than once, even in theory on the same
date), so the surrogate `id` is the only key, and every attribute depends
on it fully. **3NF.**

**Deliberate design choice:** `officers.rank_id` is **not** derived from
`promotions` via a query/view at read time — it is written directly by the
application whenever a promotion is recorded. This is a pragmatic
performance decision (every officer list/roster view needs current rank
without a correlated subquery), and it does not violate normalization
because `promotions` is a *log of events*, not a *source of truth for
current state* — the current state genuinely lives in `officers.rank_id`.
There is no redundant storage of the same fact in two places that could
disagree; `promotions.to_rank_id` for the *latest* row happens to agree
with `officers.rank_id` by application convention, not by a normalization
rule, similar to how an `orders.status` column reflects the "current" step
of an event log without being a normalization violation.

## 6. unit_assignments

**Attributes:** id, officer_id, unit_id, assignment_type, start_date,
end_date, created_at, updated_at

**FDs:**
- `id → all other attributes`

Like `promotions`, this is a history table keyed by surrogate id, with a
business rule (at most one open row per officer) enforced via a partial
unique index rather than a key constraint, since `end_date IS NULL` isn't
expressible as a normal UNIQUE constraint. **3NF.**

## 7. operations

**Attributes:** id, name, operation_type, status, lead_unit_id, start_date,
end_date, description, created_at, updated_at

**FDs:**
- `id → all other attributes`

`lead_unit_id` is an FK, not a transitively-derived unit name/type.
**3NF.**

## 8. operation_participants

**Attributes:** id, operation_id, officer_id, role_in_operation, created_at

**FDs:**
- `id → all other attributes`
- `(operation_id, officer_id) → role_in_operation, created_at` (composite
  candidate key, enforced via UNIQUE)

This is a classic many-to-many resolver table between `operations` and
`officers`, with one extra attribute (`role_in_operation`) that depends on
the *pair*, not on either FK alone — correctly modeled as a fact about the
relationship, not about either parent entity. **3NF.**

## 9. patrols

**Attributes:** id, unit_id, officer_id, patrol_date, shift, start_time,
end_time, vehicle_code, area_description, status, created_at, updated_at

**FDs:**
- `id → all other attributes`

No candidate key smaller than `id` — the same officer could plausibly patrol
the same unit on the same date across different shifts, and even
(in edge cases) have more than one patrol row on the same shift on
different vehicles, so `id` is appropriately the sole key. **3NF.**

## 10. incidents

**Attributes:** id, incident_number, incident_type, severity, status,
reported_date, location_description, reporting_officer_id,
assigned_unit_id, operation_id, description, created_at, updated_at

**FDs:**
- `id → all other attributes`
- `incident_number → id, ...` (UNIQUE)

`operation_id` is nullable — most incidents are standalone reports, not
tied to a planned operation. **3NF.**

## 11. training_sessions

**Attributes:** id, title, training_type, instructor_name, location,
start_date, end_date, capacity, created_at, updated_at

**FDs:**
- `id → all other attributes`

**3NF.**

## 12. training_attendance

**Attributes:** id, training_session_id, officer_id, attendance_status,
score, certificate_issued, created_at

**FDs:**
- `id → all other attributes`
- `(training_session_id, officer_id) → attendance_status, score,
  certificate_issued, created_at` (composite candidate key, UNIQUE)

Many-to-many resolver between `training_sessions` and `officers`, with
`score`/`certificate_issued` correctly modeled as facts about the
*attendance event*, not about the session or officer alone. **3NF.**

## 13. audit_logs

**Attributes:** id, user_id, action, table_name, record_id, old_values,
new_values, ip_address, created_at

**FDs:**
- `id → all other attributes`

`old_values`/`new_values` are JSONB — intentionally unstructured, since the
shape of a "before/after" row snapshot differs per audited table. This is
the one place where we deliberately give up columnar structure, because
the alternative (a generic EAV-style `audit_log_fields` table) would add
join overhead for a write-heavy, rarely-queried-in-bulk table without a
normalization benefit — the "denormalized" JSON blob doesn't encode any
fact that could disagree with another column. **3NF** (with a pragmatic
carve-out for the audit payload, which is not itself a structured entity).

## Summary of denormalization-style decisions

| Decision | Table | Rationale |
|---|---|---|
| `officers.rank_id` is authoritative for *current* rank; `promotions` is an independent append-only log | officers / promotions | Avoids a correlated subquery on every roster read; no data can actually "disagree" since promotions is a log, not a duplicate of current state |
| `status`/`type` columns as `TEXT + CHECK` instead of a lookup table | operations, patrols, incidents, training_sessions, training_attendance, operation_participants | These are small, fixed enumerations where a full lookup table would add a join for no query benefit; `CHECK` gives the same integrity guarantee as an FK to a lookup table |
| `old_values`/`new_values` as JSONB | audit_logs | Audit payload shape is inherently table-dependent; forcing it into columns would require a table-per-audited-table design with no real benefit |

None of these decisions introduce a partial or transitive dependency that
could put the same fact in two places able to disagree — the schema as a
whole satisfies 3NF.
