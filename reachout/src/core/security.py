import jose.jwt
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta

from reachout.src.core.config import settings


password_hash = PasswordHash.recommended()


def get_passwod_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, secret_password: str) -> bool:
    return password_hash.verify(password, secret_password)


def create_access_token(data: dict, expire_time: timedelta | None = None) -> str:
    payload = data.copy()

    if expire_time:
        expire = datetime.now(timezone.utc) + expire_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update({"exp": expire}) 

    jwt_token = jose.jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return jwt_token