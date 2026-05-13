from datetime import date, timedelta

import pytest

from app.services import timeseries as ts


def test_parts_and_regions_listing():
    parts = ts.list_parts()
    regions = ts.list_regions()
    assert "brake_pad" in parts
    assert "China" in regions
    assert ts.list_supported_sources() == parts
    assert ts.is_supported_part("brake_pad") is True
    assert ts.is_supported_region("China") is True
    assert ts.is_supported_source("brake_pad") is True
    assert ts.is_supported_part("unknown") is False


def test_generate_timeseries_is_deterministic():
    end = date(2026, 1, 31)
    a = ts.generate_timeseries("brake_pad", "China", days=10, end=end)
    b = ts.generate_timeseries("brake_pad", "China", days=10, end=end)
    assert [p.value for p in a.points] == [p.value for p in b.points]
    assert a.points[-1].timestamp == end
    assert a.points[0].timestamp == end - timedelta(days=9)


def test_generate_timeseries_validates_days():
    with pytest.raises(ValueError):
        ts.generate_timeseries("brake_pad", "China", days=0)


def test_forecast_returns_lead_day_matrix():
    anchor = date(2026, 5, 1)
    result = ts.forecast(anchor)
    assert result.anchor_date == anchor
    assert len(result.matrix.regions) == len(ts.REGIONS)
    assert len(result.matrix.parts) == len(ts.PARTS)
    assert len(result.matrix.lead_days) == len(ts.REGIONS)
    assert len(result.matrix.lead_days[0]) == len(ts.PARTS)
    cell = result.matrix.lead_days[0][0]
    assert isinstance(cell, int)
    assert 5 <= cell <= 60


def test_delivery_matrix_deterministic_for_same_anchor():
    anchor = date(2026, 6, 15)
    m1 = ts.build_delivery_matrix(anchor)
    m2 = ts.build_delivery_matrix(anchor)
    assert m1.lead_days == m2.lead_days


def test_delivery_matrix_changes_with_anchor():
    a = ts.build_delivery_matrix(date(2020, 1, 1)).lead_days
    b = ts.build_delivery_matrix(date(2035, 12, 31)).lead_days
    assert a != b
