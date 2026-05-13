from datetime import date

from pydantic import BaseModel


class TimeseriesPoint(BaseModel):
    timestamp: date
    value: float


class TimeseriesResponse(BaseModel):
    part: str
    region: str
    days: int
    points: list[TimeseriesPoint]


class DeliveryMatrix(BaseModel):
    """Rows = regions (слева), columns = parts (сверху), значения = дней до поставки от anchor_date."""

    parts: list[str]
    regions: list[str]
    lead_days: list[list[int]]


class ForecastRequest(BaseModel):
    anchor_date: date | None = None


class ForecastResponse(BaseModel):
    anchor_date: date
    matrix: DeliveryMatrix
