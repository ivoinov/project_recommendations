from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class ProductRecommendation(BaseModel):
    product_id: int
    recommendations: List[int]
class UserBase(BaseModel):
    email: EmailStr

class UserInDB(UserBase):
    hashed_password: str

class UserCreate(UserBase):
    password: str
    full_name: str = Field(..., example="John Doe")
    username: str = Field(..., example="johndoe")

class User(UserBase):
    id: int
    is_active: Optional[bool] = True

class UserInDB(UserBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
