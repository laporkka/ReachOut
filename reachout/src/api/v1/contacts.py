from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from reachout.src.api.dependencies import get_current_user
from reachout.src.core.database import get_db
from reachout.src.schemas.contact import ContactBulkUpload
from reachout.src.models.user import Manager
from reachout.src.services.contact import ContactService


router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.post("/", response_model=dict, status_code=status.HTTP_200_OK)
async def add_list_of_contacts(
    contacts_in: ContactBulkUpload,
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    response = await ContactService(db).bulk_create_contacts(payload=contacts_in, manager_id=current_user.id)

    return response