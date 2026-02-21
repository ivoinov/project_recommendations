from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from .schemas import UserSignUp, TokenResponse
from app.repositories import UserRepository, TokenRepository
from app.services import TokenService
from app.config import settings, db_settings

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
async def create_user_signup(
    user: UserSignUp = Body(...), db: Session = Depends(db_settings.get_db)
):
    user_repo = UserRepository(db)
    token_repo = TokenRepository(db)
    token_service = TokenService(token_repo)
    existing_user = user_repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    new_user = user_repo.create(user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token_service.create_access_token(
        data={"token": new_user.email, "user_id": new_user.id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token.token, "token_type": "bearer"}


@router.post("/auth", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(db_settings.get_db),
):
    user_repo = UserRepository(db)
    token_repo = TokenRepository(db)
    token_service = TokenService(token_repo)
    user = user_repo.get_user_by_email(form_data.username)
    if not user or not user_repo.verify_password(user, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = token_repo.get_by_user_id(user.id)
    # If the user does not have a token, create one
    if not access_token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_service.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}
    # If the user has a token, check if it is expired
    expires_at = access_token.expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at is not None and expires_at < datetime.now(timezone.utc):
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_service.update_expired_token(user.id, expires_delta=access_token_expires)
        return {"access_token": access_token.token, "token_type": "bearer"}
    return {"access_token": access_token.token, "token_type": "bearer"}


# TODO:: Implement me endpoint that return user info if token is valid otherwise return 401
