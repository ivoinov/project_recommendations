from fastapi import APIRouter, Depends
from models import ProductRecommendation
import joblib

router = APIRouter()

# Load the similarity matrix and product index mapping on startup
product_similarity = joblib.load('product_similarity_matrix.joblib')
index_to_product_id = joblib.load('index_to_product_id.joblib')

@router.get("/upselling-recommendations/{product_id}", response_model=ProductRecommendation)
def upselling_recommendations(product_id: int):
    # Recommendation logic based on `product_similarity` and `index_to_product_id`
    return ProductRecommendation(product_id=product_id, recommendations=[1, 2, 3])  # Mocked response
