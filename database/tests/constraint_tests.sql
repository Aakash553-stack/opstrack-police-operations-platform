-- =====================================================================
-- OpsTrack schema constraint test suite (10 scenarios)
-- Run against a freshly-loaded database/schema.sql.
-- Each scenario prints PASS/FAIL based on whether the expected outcome
-- (an error being raised, or a row surviving/cascading as expected)
-- actually occurred.
-- =====================================================================

\set ON_ERROR_STOP off
\pset pager off

-- ---- Baseline fixture data -------------------------------------------------
BEGIN;

INSERT INTO ranks (name, level) VALUES
    ('Constable', 1), ('Sergeant', 2), ('Inspector', 3), ('Superintendent', 4);

INSERT INTO units (name, unit_type) VALUES
    ('Headquarters', 'headquarters'),
    ('Central Precinct', 'precinct'),
    ('Cyber Crime Unit', 'special_unit');

INSERT INTO officers (badge_number, first_name, last_name, gender, date_of_birth, date_joined, rank_id, current_unit_id, status)
VALUES
    ('PD-100001', 'Asha', 'Rao', 'female', '1990-01-01', '2012-06-01', 1, 2, 'active'),
    ('PD-100002', 'Vikram', 'Singh', 'male', '1985-03-15', '2008-09-01', 2, 2, 'active'),
    ('PD-100003', 'Meera', 'Nair', 'other', '1992-07-20', '2015-01-10', 1, 3, 'active');

COMMIT;

\echo '=== Scenario 1: duplicate badge number (expect FK/UNIQUE violation -> FAIL insert) ==='
DO $$
BEGIN
    BEGIN
        INSERT INTO officers (badge_number, first_name, last_name, gender, date_of_birth, date_joined, rank_id, current_unit_id)
        VALUES ('PD-100001', 'Duplicate', 'Badge', 'male', '1990-01-01', '2012-06-01', 1, 2);
        RAISE NOTICE 'RESULT: FAIL (duplicate badge was allowed)';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'RESULT: PASS (unique_violation raised as expected)';
    END;
END $$;

\echo '=== Scenario 2: bad FK - nonexistent rank_id (expect FK violation) ==='
DO $$
BEGIN
    BEGIN
        INSERT INTO officers (badge_number, first_name, last_name, gender, date_of_birth, date_joined, rank_id, current_unit_id)
        VALUES ('PD-200002', 'Bad', 'FK', 'male', '1990-01-01', '2012-06-01', 999, 2);
        RAISE NOTICE 'RESULT: FAIL (bad FK was allowed)';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'RESULT: PASS (foreign_key_violation raised as expected)';
    END;
END $$;

\echo '=== Scenario 3: invalid date range on operations (end_date < start_date) ==='
DO $$
BEGIN
    BEGIN
        INSERT INTO operations (name, operation_type, lead_unit_id, start_date, end_date)
        VALUES ('Bad Dates Op', 'raid', 1, '2026-01-10', '2026-01-01');
        RAISE NOTICE 'RESULT: FAIL (invalid date range was allowed)';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'RESULT: PASS (check_violation raised as expected)';
    END;
END $$;

\echo '=== Scenario 4: duplicate operation_participants roster entry ==='
DO $$
DECLARE
    v_op_id INTEGER;
BEGIN
    INSERT INTO operations (name, operation_type, lead_unit_id, start_date)
    VALUES ('Roster Test Op', 'checkpoint', 1, '2026-02-01') RETURNING id INTO v_op_id;

    INSERT INTO operation_participants (operation_id, officer_id, role_in_operation)
    VALUES (v_op_id, 1, 'participant');

    BEGIN
        INSERT INTO operation_participants (operation_id, officer_id, role_in_operation)
        VALUES (v_op_id, 1, 'lead');
        RAISE NOTICE 'RESULT: FAIL (duplicate roster entry was allowed)';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'RESULT: PASS (unique_violation raised as expected)';
    END;
END $$;

\echo '=== Scenario 5: concurrent open unit_assignments for same officer ==='
DO $$
BEGIN
    INSERT INTO unit_assignments (officer_id, unit_id, assignment_type, start_date, end_date)
    VALUES (2, 2, 'permanent', '2020-01-01', NULL);

    BEGIN
        INSERT INTO unit_assignments (officer_id, unit_id, assignment_type, start_date, end_date)
        VALUES (2, 3, 'temporary', '2026-01-01', NULL);
        RAISE NOTICE 'RESULT: FAIL (second open assignment was allowed)';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'RESULT: PASS (partial unique index blocked second open assignment)';
    END;
END $$;

\echo '=== Scenario 6: no-op promotion (from_rank_id = to_rank_id) ==='
DO $$
BEGIN
    BEGIN
        INSERT INTO promotions (officer_id, from_rank_id, to_rank_id, promotion_date)
        VALUES (1, 1, 1, '2026-01-01');
        RAISE NOTICE 'RESULT: FAIL (no-op promotion was allowed)';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'RESULT: PASS (check_violation raised as expected)';
    END;
END $$;

\echo '=== Scenario 7: malformed badge number format ==='
DO $$
BEGIN
    BEGIN
        INSERT INTO officers (badge_number, first_name, last_name, gender, date_of_birth, date_joined, rank_id, current_unit_id)
        VALUES ('bad-badge-1', 'Malformed', 'Badge', 'male', '1990-01-01', '2012-06-01', 1, 2);
        RAISE NOTICE 'RESULT: FAIL (malformed badge number was allowed)';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'RESULT: PASS (check_violation raised as expected)';
    END;
END $$;

\echo '=== Scenario 8: restricted delete - rank referenced by an officer ==='
DO $$
BEGIN
    BEGIN
        DELETE FROM ranks WHERE name = 'Constable';
        RAISE NOTICE 'RESULT: FAIL (rank in use was deleted)';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'RESULT: PASS (foreign_key_violation blocked restricted delete)';
    END;
END $$;

\echo '=== Scenario 9: cascading delete - operation delete cascades to operation_participants ==='
DO $$
DECLARE
    v_op_id INTEGER;
    v_count INTEGER;
BEGIN
    INSERT INTO operations (name, operation_type, lead_unit_id, start_date)
    VALUES ('Cascade Test Op', 'surveillance', 1, '2026-03-01') RETURNING id INTO v_op_id;

    INSERT INTO operation_participants (operation_id, officer_id, role_in_operation)
    VALUES (v_op_id, 3, 'support');

    DELETE FROM operations WHERE id = v_op_id;

    SELECT count(*) INTO v_count FROM operation_participants WHERE operation_id = v_op_id;
    IF v_count = 0 THEN
        RAISE NOTICE 'RESULT: PASS (operation_participants rows cascaded on operation delete)';
    ELSE
        RAISE NOTICE 'RESULT: FAIL (orphaned operation_participants rows remain)';
    END IF;
END $$;

\echo '=== Scenario 10: SET NULL delete - deleting a unit nulls officers.current_unit_id ==='
DO $$
DECLARE
    v_unit_id INTEGER;
    v_officer_id INTEGER;
    v_current_unit INTEGER;
BEGIN
    INSERT INTO units (name, unit_type) VALUES ('Temp Unit For Delete Test', 'precinct') RETURNING id INTO v_unit_id;

    INSERT INTO officers (badge_number, first_name, last_name, gender, date_of_birth, date_joined, rank_id, current_unit_id)
    VALUES ('PD-300003', 'SetNull', 'Test', 'male', '1990-01-01', '2012-06-01', 1, v_unit_id)
    RETURNING id INTO v_officer_id;

    DELETE FROM units WHERE id = v_unit_id;

    SELECT current_unit_id INTO v_current_unit FROM officers WHERE id = v_officer_id;
    IF v_current_unit IS NULL THEN
        RAISE NOTICE 'RESULT: PASS (officers.current_unit_id set to NULL on unit delete)';
    ELSE
        RAISE NOTICE 'RESULT: FAIL (current_unit_id not nulled)';
    END IF;
END $$;

\echo '=== Test suite complete ==='
