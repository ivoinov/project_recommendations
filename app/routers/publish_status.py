from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache.recommendation_cache import build_cache_key, delete_cache_keys
from app.config import db_settings
from app.models import RecommendationCandidate
from app.repositories import RecommendationPublishRepository, TokenRepository
from app.routers.publish_schemas import (
    PlacementPublishStatus,
    PublishRollbackRequest,
    PublishRollbackResponse,
    PublishRunStatus,
    PublishStatusResponse,
)
from app.services import TokenService
from app.services.shop_db import get_shop_db

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
    prefix="/v1/shops/{shop_id}/publishes",
    dependencies=[Depends(verify_token)],
)


@router.get("/status", response_model=PublishStatusResponse)
def publish_status(shop_id: str, db: Session = Depends(get_shop_db)):
    publish_repo = RecommendationPublishRepository(db)
    latest_run = publish_repo.get_latest_run()
    latest_status = (
        PublishRunStatus(
            status=latest_run.status,
            run_date=latest_run.run_date,
            message=latest_run.message,
        )
        if latest_run
        else None
    )
    placements = []
    for placement in ("pdp", "cart"):
        state = publish_repo.get_state(placement)
        placements.append(
            PlacementPublishStatus(
                placement=placement,
                current_version=state.current_version if state else None,
                previous_version=state.previous_version if state else None,
                latest_run=latest_status,
            )
        )
    return PublishStatusResponse(shop_id=shop_id, placements=placements)


@router.post("/rollback", response_model=PublishRollbackResponse)
def rollback_publish(
    shop_id: str,
    payload: PublishRollbackRequest,
    db: Session = Depends(get_shop_db),
):
    publish_repo = RecommendationPublishRepository(db)
    state = publish_repo.get_state(payload.placement)
    if not state or state.previous_version is None:
        return PublishRollbackResponse(
            placement=payload.placement,
            current_version=state.current_version if state else None,
            previous_version=state.previous_version if state else None,
            rolled_back=False,
        )

    old_current = state.current_version
    old_previous = state.previous_version
    updated = publish_repo.update_publish_state(
        payload.placement,
        current_version=old_previous,
        previous_version=old_current,
    )
    _invalidate_cache_for_versions(
        db,
        shop_id,
        payload.placement,
        [updated.current_version, updated.previous_version],
    )
    return PublishRollbackResponse(
        placement=payload.placement,
        current_version=updated.current_version,
        previous_version=updated.previous_version,
        rolled_back=True,
    )


def _invalidate_cache_for_versions(db, shop_id, placement, versions):
    valid_versions = [version for version in versions if version]
    if not valid_versions:
        return 0

    seed_rows = (
        db.query(RecommendationCandidate.seed_sku)
        .filter(RecommendationCandidate.placement == placement)
        .filter(RecommendationCandidate.version.in_(valid_versions))
        .distinct()
        .all()
    )
    seed_skus = [seed_sku for (seed_sku,) in seed_rows if seed_sku]
    cache_keys = []
    for seed_sku in seed_skus:
        for version in valid_versions:
            cache_keys.append(build_cache_key(shop_id, placement, seed_sku, version))
    return delete_cache_keys(cache_keys)
