#@router.post("/users", response_model=UserResponse)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db_conn import get_db
from app.database.db_users import User
from app.schemas.users import UserCreate, UserResponse
from app.core.security import get_password_hash, get_user_by_email

#@router.post("/token", response_model=Token)
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.schemas.users import Token
from app.core.security import authenticate_user, create_access_token

#@router.get("/users/me", response_model=UserResponse)
from app.core.security import get_current_user

router = APIRouter()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="這個信箱已經被註冊過了",
        )
    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, form_data.username, form_data.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
        )
    access_token = create_access_token(data={"sub": authenticated_user.email})
    return Token(access_token=access_token, token_type="bearer")

@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user