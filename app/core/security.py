from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.db_users import User


# ============================================================
# 密碼雜湊（Password Hashing）
# 使用 Argon2 演算法，負責密碼的雜湊與驗證
# ============================================================

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證使用者輸入的明文密碼，是否與資料庫存的雜湊值相符。
    用於：登入驗證（被 authenticate_user 呼叫）"""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """把明文密碼轉換成雜湊值，供存入資料庫使用。
    用於：註冊（新增使用者時雜湊密碼）"""
    return password_hash.hash(password)


# ============================================================
# JWT Token 產生（Token Creation）
# 登入成功後，發給使用者一個有時效性的通行證
# ============================================================

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """把資料（例如使用者 email）包裝成一個簽章過、有過期時間的 JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


# ============================================================
# 資料庫查詢（User Query）
# 根據 email 查詢對應的使用者
# ============================================================

def get_user_by_email(db: Session, email: str) -> User | None:
    """用 email 查詢資料庫，回傳對應的 User，查不到則回傳 None"""
    statement = select(User).where(User.email == email)
    result = db.execute(statement)
    return result.scalar_one_or_none()


# ============================================================
# Token 驗證（Token Verification）
# 拿到一個 token，解析、驗證，並確認對應的使用者真實存在
# ============================================================

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.database.db_conn import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """
    解析並驗證 JWT token，確認發送請求的人是誰。
    驗證流程：解析 token → 取出 email → 查詢資料庫確認使用者存在
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 裡沒有 email 資訊",
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 無效或已過期",
        )

    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="找不到這個使用者",
        )

    return user

# ============================================================
# 登入驗證（User Authentication）
# 驗證帳號密碼是否正確，用於登入流程
# ============================================================

DUMMY_HASH = get_password_hash("dummypassword")


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    驗證使用者的 email 和密碼是否正確。
    即使使用者不存在，也故意執行一次密碼比對（用 DUMMY_HASH），
    確保回應時間一致，避免被用來枚舉已註冊的帳號（timing attack）。
    """
    user = get_user_by_email(db, email)
    if not user:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user