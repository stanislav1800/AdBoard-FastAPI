from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import TokenInvalidException
from app.schemas import TokenData

password_hash = PasswordHash.recommended()

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return TokenData(user_id=payload.get("sub"))
    except jwt.InvalidTokenError:
        raise TokenInvalidException

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expires_minutes))
    to_encode.update({"exp": expire, "type": ACCESS_TOKEN_TYPE})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": REFRESH_TOKEN_TYPE})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_jwt_token(token: str, token_type: str = ACCESS_TOKEN_TYPE) -> dict[str, Any]:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    if payload.get("type") != token_type:
        raise jwt.InvalidTokenError("Неверный тип токена")
    return payload

def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
