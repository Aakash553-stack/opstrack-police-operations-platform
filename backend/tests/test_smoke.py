def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_full_roster_flow(client):
    rank = client.post("/api/v1/ranks/", json={"name": "Inspector", "level": 3})
    assert rank.status_code == 201
    rank_id = rank.json()["id"]

    unit = client.post(
        "/api/v1/units/", json={"name": "Test Precinct", "unit_type": "precinct"}
    )
    assert unit.status_code == 201
    unit_id = unit.json()["id"]

    officer = client.post(
        "/api/v1/officers/",
        json={
            "badge_number": "PD-500001",
            "first_name": "Test",
            "last_name": "Officer",
            "gender": "female",
            "date_of_birth": "1990-01-01",
            "date_joined": "2012-06-01",
            "rank_id": rank_id,
            "current_unit_id": unit_id,
            "status": "active",
        },
    )
    assert officer.status_code == 201
    officer_id = officer.json()["id"]

    # duplicate badge -> 409 (DB unique constraint)
    dup = client.post(
        "/api/v1/officers/",
        json={
            "badge_number": "PD-500001",
            "first_name": "Dup",
            "last_name": "Badge",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "date_joined": "2012-06-01",
            "rank_id": rank_id,
            "current_unit_id": unit_id,
        },
    )
    assert dup.status_code == 409

    # malformed badge -> 422 (Pydantic validation before it ever hits the DB)
    bad_format = client.post(
        "/api/v1/officers/",
        json={
            "badge_number": "not-a-badge",
            "first_name": "Bad",
            "last_name": "Format",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "date_joined": "2012-06-01",
            "rank_id": rank_id,
            "current_unit_id": unit_id,
        },
    )
    assert bad_format.status_code == 422

    # restricted delete: rank still referenced by the officer -> 409
    restricted = client.delete(f"/api/v1/ranks/{rank_id}")
    assert restricted.status_code == 409

    got = client.get(f"/api/v1/officers/{officer_id}")
    assert got.status_code == 200
    assert got.json()["badge_number"] == "PD-500001"

    patched = client.patch(
        f"/api/v1/officers/{officer_id}", json={"status": "on_leave"}
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "on_leave"

    deleted = client.delete(f"/api/v1/officers/{officer_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/officers/{officer_id}")
    assert missing.status_code == 404
