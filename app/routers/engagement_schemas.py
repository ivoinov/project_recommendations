from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RecommendationEngagementCreate(BaseModel):
    placement: Literal["pdp", "cart"]
    event_type: Literal["click", "add_to_cart", "impression"]
    recommended_sku: str
    context_skus: list[str] = Field(default_factory=list)
    session_id: str | None = None
    customer_id: int | None = None
    request_id: str | None = None


class RecommendationEngagementResponse(BaseModel):
    id: int
    created_at: datetime
    placement: Literal["pdp", "cart"]
    event_type: Literal["click", "add_to_cart", "impression"]
    recommended_sku: str
    context_skus: list[str]
    session_id: str | None = None
    customer_id: int | None = None
    request_id: str | None = None


class RecommendationEngagementSummaryEntry(BaseModel):
    placement: Literal["pdp", "cart"]
    event_type: Literal["click", "add_to_cart", "impression"]
    count: int


class RecommendationEngagementSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_ts: datetime = Field(..., alias="from")
    to_ts: datetime = Field(..., alias="to")
    placement: Literal["pdp", "cart"] | None = None
    results: list[RecommendationEngagementSummaryEntry]
