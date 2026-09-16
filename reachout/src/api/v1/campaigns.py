from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from reachout.src.schemas.campaign import CampaignResponse, CampaignCreate
from reachout.src.models.user import Manager
from reachout.src.api.dependencies import get_current_user
from reachout.src.services.redis import get_redis
from reachout.src.core.database import get_db
from reachout.src.services.campaign import CampaignService


router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("/add/task", response_model=CampaignResponse, status_code=status.HTTP_202_ACCEPTED)
async def add_celery_task(
    payload: CampaignCreate,
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_cli: Redis = Depends(get_redis)
):
    response = await CampaignService(db, redis_cli).add_task(payload=payload, manager_id=current_user.id)

    return response


@router.get("/get/campaigns", response_model=list[CampaignResponse], status_code=status.HTTP_200_OK)
async def get_campaign(
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_cli: Redis = Depends(get_redis)
):
    campaigns = await CampaignService(db, redis_cli).get_all_campaigns(current_user.id)

    return campaigns


@router.get("/get/{campaign_id}", response_model=CampaignResponse, status_code=status.HTTP_200_OK)
async def get_campaign(
    campaign_id: int,
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_cli: Redis = Depends(get_redis)
):
    campaign = await CampaignService(db, redis_cli).get_campaign_by_id(campaign_id, current_user.id)

    return campaign