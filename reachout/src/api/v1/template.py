from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from reachout.src.core.database import get_db
from reachout.src.api.dependencies import get_current_user
from reachout.src.models.user import Manager
from reachout.src.services.template import TemplateService
from reachout.src.schemas.template import TemplateCreate, TemplateResponse


router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("/add/template", response_model=TemplateResponse, status_code=status.HTTP_200_OK)
async def add_template(
    payload: TemplateCreate,
    current_user: Manager = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    template = await TemplateService(db=db).add_new_template(payload=payload, manager_id=current_user.id)

    return template