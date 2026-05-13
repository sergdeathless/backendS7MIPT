"""Thin HTTP client used by Dash callbacks to talk to the FastAPI backend."""

from __future__ import annotations

import os
from typing import Any

import requests

_DEFAULT_TIMEOUT = 10


def _api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


def _api_v1(path: str) -> str:
    return f"{_api_base_url()}/api/v1{path}"


def _auth_url(path: str) -> str:
    return f"{_api_base_url()}/auth{path}"


class APIError(RuntimeError):
    pass


def login(username: str, password: str) -> str:
    """Exchange username/password for a JWT bearer token."""
    response = requests.post(
        _auth_url("/token"),
        data={"username": username, "password": password},
        timeout=_DEFAULT_TIMEOUT,
    )
    if response.status_code != 200:
        raise APIError(f"Login failed: {response.text}")
    return response.json()["access_token"]


def register(username: str, password: str) -> dict[str, Any]:
    response = requests.post(
        _auth_url("/register"),
        json={"username": username, "password": password},
        timeout=_DEFAULT_TIMEOUT,
    )
    if response.status_code not in (200, 201):
        raise APIError(f"Register failed: {response.text}")
    return response.json()


def list_parts(token: str | None = None) -> list[str]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(_api_v1("/timeseries/sources"), headers=headers, timeout=_DEFAULT_TIMEOUT)
    if response.status_code != 200:
        raise APIError(f"Failed to list parts: {response.text}")
    return response.json()


def fetch_delivery_forecast(token: str, anchor_date: str | None = None) -> dict[str, Any]:
    """POST /timeseries/forecast — матрица «дней до поставки» по каталогу."""
    payload: dict[str, Any] = {}
    if anchor_date:
        payload["anchor_date"] = anchor_date
    response = requests.post(
        _api_v1("/timeseries/forecast"),
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=_DEFAULT_TIMEOUT,
    )
    if response.status_code != 200:
        raise APIError(f"Forecast failed: {response.text}")
    return response.json()
