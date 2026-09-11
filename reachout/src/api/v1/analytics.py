from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from reachout.src.core.database import get_db
from reachout.src.api.dependencies import get_current_user
from reachout.src.services.redis import get_redis
from reachout.src.services.analytics import AnalyticService
from reachout.src.schemas.analytics import AnalyticResponse
from reachout.src.models.user import Manager

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/", response_model=AnalyticResponse, status_code=status.HTTP_200_OK)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: Manager = Depends(get_current_user),
    redis_cli: Redis = Depends(get_redis)
):
    response = await AnalyticService(db, redis_cli).get_manager_analytics(current_user.id)

    return response