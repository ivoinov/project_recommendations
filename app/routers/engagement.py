from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import db_settings
from app.models import RecommendationEvent
from app.repositories import RecommendationEventRepository, TokenRepository
from app.services import TokenService
from app.services.shop_db import get_shop_db
from app.routers.engagement_schemas import (
    RecommendationEngagementCreate,
    RecommendationEngagementResponse,
    RecommendationEngagementSummaryEntry,
    RecommendationEngagementSummaryResponse,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


def verify_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(db_settings.get_db, use_cache=False),
):
    token_service = TokenService(TokenRepository(db))
    current_path = db.execute(text("SHOW search_path")).scalar()
    try:
        db.execute(text("SET search_path TO public"))
        if not token_service.verify_token(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    finally:
        if current_path:
            db.execute(text(f"SET search_path TO {current_path}"))


router = APIRouter(
    prefix="/v1/shops/{shop_id}/engagement",
    dependencies=[Depends(verify_token)],
)


def _parse_context_skus(context_skus: str | None) -> list[str]:
    if not context_skus:
        return []
    return [sku for sku in context_skus.split(",") if sku]


@router.post(
    "/recommendations", response_model=RecommendationEngagementResponse, status_code=200
)
def log_recommendation_engagement(
    shop_id: str,
    payload: RecommendationEngagementCreate,
    db: Session = Depends(get_shop_db),
):
    repo = RecommendationEventRepository(db)
    context_skus = ",".join(payload.context_skus) if payload.context_skus else ""
    event = RecommendationEvent(
        placement=payload.placement,
        event_type=payload.event_type,
        context_skus=context_skus,
        recommended_sku=payload.recommended_sku,
        session_id=payload.session_id,
        customer_id=payload.customer_id,
        request_id=payload.request_id,
    )
    saved = repo.create(event)
    return RecommendationEngagementResponse(
        id=saved.id,
        created_at=saved.created_at,
        placement=saved.placement,
        event_type=saved.event_type,
        recommended_sku=saved.recommended_sku,
        context_skus=_parse_context_skus(saved.context_skus),
        session_id=saved.session_id,
        customer_id=saved.customer_id,
        request_id=saved.request_id,
    )


@router.get(
    "/recommendations/summary",
    response_model=RecommendationEngagementSummaryResponse,
)
def recommendation_engagement_summary(
    shop_id: str,
    from_ts: datetime = Query(..., alias="from"),
    to_ts: datetime = Query(..., alias="to"),
    placement: Literal["pdp", "cart"] | None = Query(None),
    db: Session = Depends(get_shop_db),
):
    repo = RecommendationEventRepository(db)
    rows = repo.count_by_placement_and_type(from_ts, to_ts, placement)
    results = [RecommendationEngagementSummaryEntry(**row) for row in rows]
    return RecommendationEngagementSummaryResponse(
        from_ts=from_ts,
        to_ts=to_ts,
        placement=placement,
        results=results,
    )
