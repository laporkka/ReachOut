from jose import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from redis.asyncio import Redis
from jose import JWTError

from reachout.src.core.database import get_db
from reachout.src.models.user import Manager
from reachout.src.core.config import settings
from reachout.src.services.redis import get_redis
from reachout.src.core.exeptions import InvalidCredentialsError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/managers/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
        redis_cli: Redis = Depends(get_redis)
) -> Manager:
    try:
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)

        jti: str | None = payload.get("jti")
        email: EmailStr | None = payload.get("sub")

        if not email or not jti:
            raise InvalidCredentialsError()
            
    except JWTError:
        raise InvalidCredentialsError()

    is_blacklisted = await redis_cli.get(f"blacklist:{jti}")
    
    if is_blacklisted is not None:
        raise InvalidCredentialsError()

    query = select(Manager).filter(Manager.email == email)
    result = await db.execute(query)
    manager = result.scalar_one_or_none()

    if not manager:
        raise InvalidCredentialsError()

    return manager