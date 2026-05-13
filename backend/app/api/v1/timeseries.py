from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.timeseries_request import TimeseriesRequest
from app.models.user import User
from app.schemas.timeseries import (
    ForecastRequest,
    ForecastResponse,
    TimeseriesResponse,
)
from app.services import timeseries as ts_service

router = APIRouter(prefix="/timeseries", tags=["timeseries"])


@router.get("/sources", response_model=list[str])
def list_sources() -> list[str]:
    """Parts catalog (legacy path name)."""
    return ts_service.list_parts()


@router.get("/regions", response_model=list[str])
def list_regions() -> list[str]:
    return ts_service.list_regions()


@router.get("", response_model=TimeseriesResponse)
def get_timeseries(
    part: str = Query(..., min_length=1, max_length=64),
    region: str = Query(..., min_length=1, max_length=64),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TimeseriesResponse:
    if not ts_service.is_supported_part(part):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported part. Available: {ts_service.list_parts()}",
        )
    if not ts_service.is_supported_region(region):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported region. Available: {ts_service.list_regions()}",
        )
    src_key = f"{part}|{region}"[:64]
    db.add(
        TimeseriesRequest(
            user_id=current_user.id,
            source=src_key,
            days=days,
        )
    )
    db.commit()
    return ts_service.generate_timeseries(part, region, days)


@router.post("/forecast", response_model=ForecastResponse)
def forecast(
    payload: ForecastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ForecastResponse:
    anchor = payload.anchor_date or date.today()
    db.add(
        TimeseriesRequest(
            user_id=current_user.id,
            source="parts_delivery",
            # Internal log key: Proleptic Gregorian day index (not shown in UI).
            days=anchor.toordinal(),
            forecast_horizon=None,
        )
    )
    db.commit()
    return ts_service.forecast(anchor=anchor)


@router.get("/admin/recent", response_model=list[dict])
def admin_recent_requests(
    limit: int = Query(20, ge=1, le=200),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = (
        db.query(TimeseriesRequest)
        .order_by(TimeseriesRequest.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": row.id,
            "user_id": row.user_id,
            "source": row.source,
            "days": row.days,
            "forecast_horizon": row.forecast_horizon,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
