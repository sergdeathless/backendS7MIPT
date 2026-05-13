def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_sources_endpoint_lists_parts(client):
    response = client.get("/api/v1/timeseries/sources")
    assert response.status_code == 200
    assert "brake_pad" in response.json()


def test_regions_endpoint_lists_regions(client):
    response = client.get("/api/v1/timeseries/regions")
    assert response.status_code == 200
    assert "China" in response.json()


def test_timeseries_requires_auth(client):
    response = client.get(
        "/api/v1/timeseries",
        params={"part": "brake_pad", "region": "China", "days": 7},
    )
    assert response.status_code == 401


def test_timeseries_returns_points(client, auth_token):
    response = client.get(
        "/api/v1/timeseries",
        params={"part": "brake_pad", "region": "China", "days": 14},
        headers=_auth_headers(auth_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["part"] == "brake_pad"
    assert body["region"] == "China"
    assert body["days"] == 14
    assert len(body["points"]) == 14


def test_timeseries_rejects_unknown_part(client, auth_token):
    response = client.get(
        "/api/v1/timeseries",
        params={"part": "mars", "region": "China", "days": 7},
        headers=_auth_headers(auth_token),
    )
    assert response.status_code == 400


def test_timeseries_rejects_unknown_region(client, auth_token):
    response = client.get(
        "/api/v1/timeseries",
        params={"part": "brake_pad", "region": "mars", "days": 7},
        headers=_auth_headers(auth_token),
    )
    assert response.status_code == 400


def test_forecast_returns_lead_days_matrix(client, auth_token):
    response = client.post(
        "/api/v1/timeseries/forecast",
        json={"anchor_date": "2026-05-01"},
        headers=_auth_headers(auth_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["anchor_date"] == "2026-05-01"
    assert "matrix" in body
    assert "lead_days" in body["matrix"]
    assert len(body["matrix"]["lead_days"]) >= 1
    assert isinstance(body["matrix"]["lead_days"][0][0], int)


def test_forecast_empty_body_ok(client, auth_token):
    response = client.post(
        "/api/v1/timeseries/forecast",
        json={},
        headers=_auth_headers(auth_token),
    )
    assert response.status_code == 200
    assert "matrix" in response.json()


def test_forecast_rejects_bad_anchor(client, auth_token):
    response = client.post(
        "/api/v1/timeseries/forecast",
        json={"anchor_date": "not-a-date"},
        headers=_auth_headers(auth_token),
    )
    assert response.status_code == 422


def test_admin_endpoint_requires_admin_role(client, auth_token):
    response = client.get(
        "/api/v1/timeseries/admin/recent",
        headers=_auth_headers(auth_token),
    )
    assert response.status_code == 403


def test_admin_endpoint_lists_recent(client, admin_token, auth_token):
    client.get(
        "/api/v1/timeseries",
        params={"part": "brake_pad", "region": "USA", "days": 5},
        headers=_auth_headers(auth_token),
    )
    response = client.get(
        "/api/v1/timeseries/admin/recent",
        params={"limit": 10},
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) >= 1
    assert rows[0]["source"] == "brake_pad|USA"
