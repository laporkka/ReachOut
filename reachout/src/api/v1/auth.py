from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from jose import jwt, JWTError
from datetime import datetime, timezone

from reachout.src.schemas.auth import Token, ManagerCreate, ManagerResponse
from reachout.src.models.user import Manager
from reachout.src.core.database import get_db
from reachout.src.core.security import get_passwod_hash, verify_password, create_access_token
from reachout.src.api.dependencies import get_current_user
from reachout.src.services.redis import get_redis
from reachout.src.core.config import settings


router = APIRouter(prefix="/managers", tags=["Managers"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/managers/login")


@router.post("/register", response_model=ManagerResponse, status_code=status.HTTP_201_CREATED)
async def manager_register(
    manager_in: ManagerCreate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Manager).filter(Manager.email == manager_in.email)
    result = await db.execute(query)
    exist_manager = result.scalar_one_or_none()

    if exist_manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist"
        )

    new_manager = Manager(
        email=manager_in.email,
        hashed_password=get_passwod_hash(manager_in.password),
        is_active=True
    )

    db.add(new_manager)
    await db.commit()
    await db.refresh(new_manager)

    return new_manager


@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
async def manager_login(
    manager_in: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(Manager).filter(Manager.email == manager_in.username)
    result = await db.execute(query)
    manager = result.scalar_one_or_none()

    if not manager or not verify_password(manager_in.password, manager.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password"
        )

    access_token = create_access_token(
        {
            "sub": manager.email,
            "role": "manager"
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: Manager = Depends(get_current_user),
    redis_cli: Redis = Depends(get_redis)
):
    try:    
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        
        jti: str | None = payload.get("jti")
        exp: int | None = payload.get("exp")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token state during logout request"
        )

    current_time = int(datetime.now(timezone.utc).timestamp())
    remainig_seconds = exp - current_time

    if remainig_seconds > 0:
        await redis_cli.set(
            f"blacklist:{jti}",
            value="revoked",
            ex=remainig_seconds
        )

    return {"detail": "Successfully logged out. Session terminated safely."}
