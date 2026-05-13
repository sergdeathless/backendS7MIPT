"""Synthetic spare-parts delivery stub.

Deterministic lead times (days from order date to expected delivery) per
(part, region). Not a trained model; mimics API contracts for a logistics UI.
"""

from __future__ import annotations

import hashlib
import math
from datetime import date, timedelta

from app.schemas.timeseries import (
    DeliveryMatrix,
    ForecastResponse,
    TimeseriesPoint,
    TimeseriesResponse,
)

# Catalogs used by the stub (slugs stable for API tests).
PARTS: tuple[str, ...] = (
    "brake_pad",
    "oil_filter",
    "spark_plug",
    "timing_belt",
    "battery",
    "radiator_hose",
    "wiper_blade",
    "air_filter",
    "cabin_filter",
    "alternator",
    "starter",
    "fuel_filter",
    "shock_absorber",
    "wheel_bearing",
    "cv_joint",
    "clutch_disc",
    "thermostat",
    "water_pump",
    "ignition_coil",
    "lambda_sensor",
)
REGIONS: tuple[str, ...] = (
    "China",
    "USA",
    "India",
    "Turkey",
    "Russia",
)


def list_parts() -> list[str]:
    return list(PARTS)


def list_regions() -> list[str]:
    return list(REGIONS)


def list_supported_sources() -> list[str]:
    """Backward-compatible alias: sources meant «parts» for legacy routes."""
    return list_parts()


def is_supported_part(part: str) -> bool:
    return part in PARTS


def is_supported_region(region: str) -> bool:
    return region in REGIONS


def is_supported_source(part: str) -> bool:
    """Legacy name: treat string as a part id."""
    return is_supported_part(part)


def _seed(part: str, region: str, salt: str = "") -> float:
    digest = hashlib.sha256(f"{part}:{region}:{salt}".encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _base_lead_days(part: str, region: str) -> int:
    """Days from order date until delivery (5–60), stable per (part, region)."""
    digest = hashlib.sha256(f"{part}:{region}".encode()).hexdigest()
    return 5 + int(digest[:8], 16) % 56


def _lead_days_series(part: str, region: str, day_offset: int) -> float:
    """Slightly varying lead time for synthetic «history» rows."""
    base = float(_base_lead_days(part, region))
    wobble = 3.0 * math.sin(2 * math.pi * day_offset / 12.0)
    noise = (_seed(part, region, str(day_offset)) - 0.5) * 2.0
    return round(base + wobble + noise, 4)


def _lead_days_for_anchor(anchor: date, part: str, region: str) -> int:
    """Base lead time plus deterministic shift from order date (stub logistics noise)."""
    base = _base_lead_days(part, region)
    digest = hashlib.sha256(f"{anchor.isoformat()}|{part}|{region}".encode()).hexdigest()
    delta = int(digest[:6], 16) % 17 - 8  # roughly -8..+8
    return min(60, max(3, base + delta))


def build_delivery_matrix(anchor: date) -> DeliveryMatrix:
    """Rows follow ``REGIONS``, columns follow ``PARTS``; cells = days until delivery from ``anchor``."""
    lead_days: list[list[int]] = []
    for region in REGIONS:
        row = [_lead_days_for_anchor(anchor, part, region) for part in PARTS]
        lead_days.append(row)
    return DeliveryMatrix(
        parts=list(PARTS),
        regions=list(REGIONS),
        lead_days=lead_days,
    )


def generate_timeseries(
    part: str,
    region: str,
    days: int,
    end: date | None = None,
) -> TimeseriesResponse:
    """Synthetic daily «promised lead time» samples ending on ``end`` (default: today)."""
    if days < 1:
        raise ValueError("days must be >= 1")
    end_day = end or date.today()
    points: list[TimeseriesPoint] = []
    for offset in range(days):
        day = end_day - timedelta(days=days - 1 - offset)
        points.append(
            TimeseriesPoint(
                timestamp=day,
                value=_lead_days_series(part, region, offset),
            )
        )
    return TimeseriesResponse(part=part, region=region, days=days, points=points)


def forecast(anchor: date) -> ForecastResponse:
    """Full-catalog matrix: each cell is days from ``anchor`` until expected delivery."""
    return ForecastResponse(anchor_date=anchor, matrix=build_delivery_matrix(anchor))
