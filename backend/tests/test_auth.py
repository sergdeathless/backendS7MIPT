from app.auth.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("hunter2")
    assert hashed != "hunter2"
    assert verify_password("hunter2", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_jwt_roundtrip():
    token, expires_in = create_access_token("alice", "user")
    assert expires_in > 0
    payload = decode_token(token)
    assert payload["sub"] == "alice"
    assert payload["role"] == "user"


def test_register_and_login_flow(client):
    register_response = client.post(
        "/auth/register",
        json={"username": "bob", "password": "secret123"},
    )
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["username"] == "bob"
    assert body["role"] == "user"

    duplicate = client.post(
        "/auth/register",
        json={"username": "bob", "password": "secret123"},
    )
    assert duplicate.status_code == 409

    bad_login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "WRONG"},
    )
    assert bad_login.status_code == 401

    good_login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "secret123"},
    )
    assert good_login.status_code == 200
    token = good_login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "bob"


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401
