from pydantic import BaseModel
from typing import List

class ProductRecommendation(BaseModel):
    product_id: int
    recommendations: List[int]
