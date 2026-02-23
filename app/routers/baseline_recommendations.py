from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import db_settings
from app.repositories import TokenRepository, ProductRepository
from app.services import TokenService
from app.services.precomputed_recommendation_service import (
    get_cart_recommendations,
    get_pdp_recommendations,
)
from app.services.shop_db import get_shop_db
from app.routers.baseline_schemas import (
    CartRecommendationRequest,
    BaselineRecommendationResponse,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


def verify_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(db_settings.get_db)
):
    token_service = TokenService(TokenRepository(db))
    if not token_service.verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


router = APIRouter(
    prefix="/v1/shops/{shop_id}/recommendations",
    dependencies=[Depends(verify_token)],
)


@router.get("/pdp/{product_sku}", response_model=BaselineRecommendationResponse)
def pdp_recommendations(
    shop_id: str,
    product_sku: str,
    db: Session = Depends(get_shop_db),
):
    product_repo = ProductRepository(db)
    result = get_pdp_recommendations(
        shop_id=shop_id,
        seed_sku=product_sku,
        db=db,
        product_repository=product_repo,
    )
    return BaselineRecommendationResponse(
        placement="pdp",
        seed_skus=result["seed_skus"],
        co_purchase=result["co_purchase"],
        content_based=result["content_based"],
        recommendations=result["recommendations"],
    )


@router.post("/cart", response_model=BaselineRecommendationResponse)
def cart_recommendations(
    shop_id: str,
    payload: CartRecommendationRequest,
    db: Session = Depends(get_shop_db),
):
    product_repo = ProductRepository(db)
    result = get_cart_recommendations(
        shop_id=shop_id,
        seed_skus=payload.cart_skus,
        db=db,
        product_repository=product_repo,
        exclude_skus=payload.exclude_skus,
        limit=payload.limit,
    )
    return BaselineRecommendationResponse(
        placement="cart",
        seed_skus=result["seed_skus"],
        co_purchase=result["co_purchase"],
        content_based=result["content_based"],
        recommendations=result["recommendations"],
    )
