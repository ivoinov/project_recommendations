from .schemas import ProductRecommendationResponse
from app.models import ProductRecommendation, Token
import os.path
import pickle
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db, get_product_by_sku, get_product_skus_by_ids
from datetime import datetime
from sklearn.metrics.pairwise import linear_kernel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Load the similarity matrix and product index mapping on startup
# product_similarity = joblib.load('product_similarity_matrix.joblib')
# index_to_product_id = joblib.load('index_to_product_id.joblib')


def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token = db.query(Token).filter(Token.token == token).first()
    if not token or token.expires_at < datetime.utcnow():
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
    product_sku: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # Verify the token
    verify_token(token, db)
    # TODO: Implement load getting traning model from the helper file to take into account if file exists.
    # Load the trained SVD model from a file
    if os.path.isfile("trained_svd_model.pkl") and os.path.isfile(
        "svd_model_trainset.pkl"
    ):
        with open("trained_svd_model.pkl", "rb") as file:
            trained_svd_model = pickle.load(file)
            trainset = pickle.load(open("svd_model_trainset.pkl", "rb"))
            # Get the internal ID of the product
            product = get_product_by_sku(product_sku)
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
    product_sku: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # Verify the token
    verify_token(token, db)
    # TODO: Move load traning model from the helper to take into account if file exists.
    if os.path.isfile("tfidf_matrices.pkl"):
        # Load saved TF-IDF matrices and vectorizers from file
        with open("tfidf_matrices.pkl", "rb") as file:
            tfidf_matrices = pickle.load(file)
            product = get_product_by_sku(product_sku)
            if product and product.parent_category in tfidf_matrices:
                tfidf_matrix = tfidf_matrices[product.parent_category]["tfidf_matrix"]
                tfidf_vectorizer = tfidf_matrices[product.parent_category][
                    "tfidf_vectorizer"
                ]
                # Compute TF-IDF matrix for the product description
                product_tfidf = tfidf_vectorizer.transform([product.description])
                # Compute the cosine similarity between the product and all other products
                cosine_similarities = linear_kernel(
                    product_tfidf, tfidf_matrix
                ).flatten()
                # Get the index of the most similar products
                similar_indices = cosine_similarities.argsort()[:-6:-1]
                internal_ids = []
                for index, value in enumerate(similar_indices):
                    internal_ids.append(value)
                # Get the SKUs of the most similar products
                similar_product_skus = [
                    product.sku for product in get_product_skus_by_ids(internal_ids)
                ]
                return ProductRecommendation(
                    product_sku=product_sku, recommendations=similar_product_skus
                )
    return ProductRecommendation(product_sku=product_sku, recommendations=[])
