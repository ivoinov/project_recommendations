from pydantic import BaseModel, EmailStr, Field


class UserSignUp(BaseModel):
    username: str = Field(
        ...,
        description="Username of the user",
        examples=["john_doe"],
        min_length=3,
        max_length=50,
    )
    email: EmailStr = Field(
        ..., description="Email of the user", examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="Password of the user",
        examples=["password"],
        min_length=8,
        max_length=50,
    )
    full_name: str = Field(
        ...,
        description="Full name of the user",
        examples=["John Doe"],
        min_length=3,
        max_length=50,
    )
    disabled: bool = None


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="Access token for the user",
        examples=[
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjIyNzIwMzIyfQ.3J"
        ],
    )
    token_type: str = Field(..., description="Type of token", examples=["bearer"])


class ProductRecommendationResponse(BaseModel):
    product_sku: str = Field(
        ..., description="Product SKU of the product", examples=[1]
    )
    recommendations: list[str] = Field(
        ..., description="List of recommended product SKUs", examples=[[1, 2, 3]]
    )
