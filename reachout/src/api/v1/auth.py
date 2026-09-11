from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from reachout.src.schemas.auth import Token, ManagerCreate, ManagerResponse
from reachout.src.models.user import Manager
from reachout.src.core.database import get_db
from reachout.src.api.dependencies import get_current_user
from reachout.src.services.redis import get_redis
from reachout.src.services.auth import AuthService
from reachout.src.core.config import settings


router = APIRouter(prefix="/managers", tags=["Managers"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/managers/login")


@router.post("/register", response_model=ManagerResponse, status_code=status.HTTP_201_CREATED)
async def manager_register(
    manager_in: ManagerCreate,
    db: AsyncSession = Depends(get_db)
):
    new_manager = await AuthService(db).manager_register(manager_in)
    return new_manager


@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
async def manager_login(
    manager_in: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    access_token = await AuthService(db).manager_login(manager_in)
    return access_token
    

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: Manager = Depends(get_current_user),
    redis_cli: Redis = Depends(get_redis)
):
    return await AuthService().manager_logout(token, redis_cli) 