from .schemas import ProductRecommendationResponse
from app.models import ProductRecommendation
import os
import pickle
import numpy as np
import pandas as pd
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import linear_kernel
from app.config import settings, db_settings
from app.repositories import TokenRepository, ProductRepository
from app.services import TokenService

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


router = APIRouter(dependencies=[Depends(verify_token)])


@router.get(
    "/upselling-recommendations/{product_sku}",
    response_model=ProductRecommendationResponse,
)
def upselling_recommendations(
    product_sku: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(db_settings.get_db),
):
    product_repo = ProductRepository(db)
    # TODO: Implement load getting traning model from the helper file to take into account if file exists.
    # Load the trained SVD model from a file
    if os.path.isfile("trained_svd_model.pkl") and os.path.isfile(
        "svd_model_trainset.pkl"
    ):
        with open("trained_svd_model.pkl", "rb") as file:
            trained_svd_model = pickle.load(file)
            trainset = pickle.load(open("svd_model_trainset.pkl", "rb"))
            # Get the internal ID of the product
            product = product_repo.search_by_attribute("sku", product_sku)[0]
            if product is not None:
                predictions = [
                    trained_svd_model.predict(product.sku, _).est
                    for _ in range(trainset.n_items)
                ]
                top_n_svd = [
                    (trainset.to_raw_iid(inner_id), prediction)
                    for inner_id, prediction in enumerate(predictions)
                ]
                top_n_svd = sorted(top_n_svd, key=lambda x: x[1], reverse=True)[:10]
                top_n_product_ids_svd = [item_id for item_id, _ in top_n_svd]
                return ProductRecommendation(
                    product_sku=product_sku, recommendations=top_n_product_ids_svd
                )
    # Recommendation logic based on `product_similarity` and `index_to_product_id`
    return ProductRecommendation(
        product_sku=product_sku, recommendations=[]
    )  # Mocked response


@router.get(
    "/similar-recommendations/{product_sku}",
    response_model=ProductRecommendationResponse,
)
def similar_recommendations(
    product_sku: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(db_settings.get_db),
):
    product_repo = ProductRepository(db)
    text_weight = 0.7
    price_weight = 0.2
    if settings.description_tfidf_matrices is not None:
        product = product_repo.search_by_attribute("sku", product_sku)[0]
        if product and product.parent_category in settings.description_tfidf_matrices:
            category_id = product.parent_category
            index = _get_iloc(product.sku, category_id, product_repo)

            cosine_sim = _calculate_sim(category_id)
            combined_similarity = text_weight * cosine_sim + price_weight * np.outer(
                settings.price_vectors[category_id], settings.price_vectors[category_id]
            )
            similar_product_skus = _get_recommendations(
                index, combined_similarity, category_id, product_repo
            )

            return ProductRecommendation(
                product_sku=product_sku, recommendations=similar_product_skus
            )
    return ProductRecommendation(product_sku=product_sku, recommendations=[])


def _get_iloc(product_sku, category_id, product_repo):
    products = product_repo.search_by_attribute("parent_category", category_id)
    df_filtered = pd.DataFrame([product.as_dict() for product in products])
    return df_filtered[df_filtered["sku"] == product_sku].index[0]


def _calculate_sim(category_id):
    return linear_kernel(
        settings.description_tfidf_matrices[category_id]["tfidf_matrix"],
        settings.description_tfidf_matrices[category_id]["tfidf_matrix"],
    )


def _get_recommendations(product_index, cosine_sim, category_id, product_repo):
    sim_scores = list(enumerate(cosine_sim[product_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:21]  # Get top 20
    sim_indices = [i[0] for i in sim_scores]
    return [
        product_repo.search_by_attribute("parent_category", category_id)[i].sku
        for i in sim_indices
    ]
