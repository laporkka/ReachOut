from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from reachout.src.models.template import Template
from reachout.src.schemas.template import TemplateCreate, TemplateResponse


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def add_new_template(self, payload: TemplateCreate, manager_id: int) -> TemplateResponse:
        query = select(Template).filter(Template.title == payload.title)
        result = await self.db.execute(query)
        template = result.scalar_one_or_none()

        if template:
            return

        new_template = Template(
            manager_id=manager_id,
            title=payload.title,
            body=payload.body
        )

        self.db.add(new_template)
        await self.db.commit()
        await self.db.refresh(new_template)

        return new_template


    async def get_all_templates(self, manager_id: int) -> List[TemplateResponse]:
        query = select(Template).filter(Template.manager_id == manager_id)
        result = await self.db.execute(query)
        templates = result.scalars().all()

        return templates