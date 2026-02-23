from datetime import date
from typing import Literal

from pydantic import BaseModel


class PublishRunStatus(BaseModel):
    status: str | None = None
    run_date: date | None = None
    message: str | None = None


class PlacementPublishStatus(BaseModel):
    placement: Literal["pdp", "cart"]
    current_version: int | None = None
    previous_version: int | None = None
    latest_run: PublishRunStatus | None = None


class PublishStatusResponse(BaseModel):
    shop_id: str
    placements: list[PlacementPublishStatus]


class PublishRollbackRequest(BaseModel):
    placement: Literal["pdp", "cart"]


class PublishRollbackResponse(BaseModel):
    placement: Literal["pdp", "cart"]
    current_version: int | None = None
    previous_version: int | None = None
    rolled_back: bool
