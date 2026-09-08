from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from reachout.src.schemas.campaign import CampaignCreate
from reachout.src.models.campaign import Campaign, StatusEnum
from reachout.src.models.contact import Contact
from reachout.src.tasks.celery_app import celery_app


class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def add_task(self, payload: CampaignCreate, manager_id: int):
        query = select(func.count(Contact.manager_id).filter(Contact.manager_id == manager_id, Contact.tags.any(payload.target_tag)))
        result = await self.db.execute(query)
        calculated_total_count = result.scalar_one_or_none()

        new_campaign = Campaign(
            manager_id=manager_id,
            template_id=payload.template_id,
            target_tag=payload.target_tag,
            scheduled_at=payload.scheduled_at,
            status=StatusEnum.PENDING,
            total_recipients=calculated_total_count         
        )

        self.db.add(new_campaign)
        await self.db.commit()
        await self.db.refresh(new_campaign)

        celery_app.send_task(
            "src.tasks.campaign_tasks.send_mass_email_task",
            kwargs={"campaign_id": new_campaign.id}
        )

        return new_campaign