from .schemas import ProductRecommendationResponse
from models import ProductRecommendation, Token
import joblib
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime

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
@router.get("/upselling-recommendations/{product_id}", response_model=ProductRecommendationResponse)
def upselling_recommendations(product_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Verify the token
    verify_token(token, db)
    # Recommendation logic based on `product_similarity` and `index_to_product_id`
    return ProductRecommendation(product_id=product_id, recommendations=[1, 2, 3])  # Mocked response