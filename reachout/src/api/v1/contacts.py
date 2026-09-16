from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from reachout.src.api.dependencies import get_current_user
from reachout.src.core.database import get_db
from reachout.src.services.redis import get_redis
from reachout.src.schemas.contact import ContactBulkUpload, ContactResponse
from reachout.src.models.user import Manager
from reachout.src.services.contact import ContactService


router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.post("/add/contacts", response_model=dict, status_code=status.HTTP_200_OK)
async def add_list_of_contacts(
    contacts_in: ContactBulkUpload,
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_cli: Redis = Depends(get_redis)
):
    response = await ContactService(db, redis_cli).bulk_create_contacts(payload=contacts_in, manager_id=current_user.id)

    return response


@router.get("/get/contacts", response_model=list[ContactResponse], status_code=status.HTTP_200_OK)
async def get_campaign(
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_cli: Redis = Depends(get_redis)
):
    contacts = await ContactService(db, redis_cli).get_all_contacts(current_user.id)

    return contacts