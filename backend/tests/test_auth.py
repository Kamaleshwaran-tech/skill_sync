import time
from app.database.session import SessionLocal


def test_register_and_login(client):
    # register
    payload = {"email": "alice@example.com", "password": "s3cureP@ssword", "full_name": "Alice"}
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "alice@example.com"
    assert "hashed_password" not in data

    # duplicate
    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 400

    # login success
    r3 = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "s3cureP@ssword"})
    assert r3.status_code == 200
    tokens = r3.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    # protected endpoint
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"

    # invalid credentials
    r4 = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "wrong"})
    assert r4.status_code == 401

    # refresh token
    r5 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r5.status_code == 200
    tokens2 = r5.json()
    assert tokens2["access_token"] != access
    assert tokens2["refresh_token"] != refresh

    # old refresh should be revoked
    r6 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r6.status_code == 401

    # logout using newest refresh
    r7 = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens2["refresh_token"]},
        headers={"Authorization": f"Bearer {tokens2['access_token']}"},
    )
    assert r7.status_code == 200

    revoked_access = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens2['access_token']}"})
    assert revoked_access.status_code == 401

    # after logout, refresh fails
    r8 = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens2["refresh_token"]})
    assert r8.status_code == 401


def test_invalid_password_registration(client):
    r = client.post("/api/v1/auth/register", json={"email": "bob@example.com", "password": "short", "full_name": "Bob"})
    assert r.status_code == 422
