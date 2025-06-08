import uuid
from datetime import timedelta, datetime, timezone

import jwt
from passlib.context import CryptContext

from common.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str | None:
    """
    密码加密，返回哈希值
    """
    if not password:
        return None
    return pwd_context.hash(password)

def verify_password(*, password: str, hashed_password: str) -> bool:
    """
    密码校验，返回 True / False
    """
    return pwd_context.verify(password, hashed_password)

def create_jwt_token(user_id: uuid.UUID, expires_delta: timedelta) -> str:
    """
    创建 JWT Token
    """
    to_encode = {
        "exp": int((datetime.now(timezone.utc) + expires_delta).timestamp()),
        "sub": str(user_id),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def parse_jwt_token(token: str) -> dict:
    """
    验证 JWT Token 成功则返回UUID

    抛出异常：
    - jose.ExpiredSignatureError: Token 已过期
    - jose.JWTError: Token 无效
    - KeyError: 缺少 "sub" 字段（无UUID？）
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload