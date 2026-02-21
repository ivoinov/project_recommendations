from typing import Literal

from pydantic import BaseModel, Field


class CartRecommendationRequest(BaseModel):
    cart_skus: list[str] = Field(..., description="List of cart SKUs")
    exclude_skus: list[str] = Field(default_factory=list)
    limit: int = Field(20, ge=1, le=100)


class BaselineRecommendationResponse(BaseModel):
    placement: Literal["pdp", "cart"]
    seed_skus: list[str]
    co_purchase: list[str]
    content_based: list[str]
    recommendations: list[str]
