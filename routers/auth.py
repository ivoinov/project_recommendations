from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from database import create_user, get_user_by_email, get_db, verify_password, get_token_by_user_id
from dependencies import create_access_token, update_access_token
import os
from dotenv import load_dotenv
from .schemas import UserSignUp, TokenResponse
from datetime import datetime

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
router = APIRouter()

@router.post("/signup", response_model=TokenResponse)
async def create_user_signup(user: UserSignUp = Body(...), db: Session = Depends(get_db)):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    new_user = await create_user(db, user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        db, data={"sub": new_user.email, "user_id": new_user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await get_token_by_user_id(db, user.id)
    # If the user does not have a token, create one
    if not access_token:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            db, data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    # If the user has a token, check if it is expired
    if access_token.expires_at < datetime.utcnow():
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await update_access_token(
            db, data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    return {"access_token": access_token.token, "token_type": "bearer"}
