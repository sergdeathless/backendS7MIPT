from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import get_settings
from app.db.session import get_db


def _sign(payload: dict) -> str:
    settings = get_settings()
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def test_token_without_subject_is_rejected(client):
    token = _sign(
        {"role": "user", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    )
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_token_for_unknown_user_is_rejected(client):
    token = _sign(
        {
            "sub": "ghost",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        }
    )
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_get_db_yields_and_closes_session():
    gen = get_db()
    session = next(gen)
    try:
        assert session is not None
    finally:
        with pytest.raises(StopIteration):
            next(gen)
