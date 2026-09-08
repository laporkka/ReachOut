from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from reachout.src.schemas.campaign import CampaignResponse, CampaignCreate
from reachout.src.models.user import Manager
from reachout.src.api.dependencies import get_current_user
from reachout.src.services.campaign import CampaignService
from reachout.src.core.database import get_db


router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("/add/task", response_model=CampaignResponse, status_code=status.HTTP_202_ACCEPTED)
async def add_celery_task(
    payload: CampaignCreate,
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    response = await CampaignService(db=db).add_task(payload=payload, manager_id=current_user.id)

    return response
