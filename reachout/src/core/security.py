import jose.jwt
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta

from reachout.src.core.config import settings


pwd_encode = CryptContext(schemes=["bcrypt"])


def get_passwod_hash(password: str) -> str:
    return pwd_encode.hash(password)


def verify_password(password: str, secret_password: str) -> bool:
    return pwd_encode.verify(secret_password, password)


def create_access_token(data: dict, expire_time: timedelta | None = None) -> str:
    payload = data.copy()

    if expire_time:
        expire = datetime.now(timezone.utc) + expire_time
    else:
        expire = datetime.noe(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update = {"exp": expire}

    jwt_token = jose.jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return jwt_token