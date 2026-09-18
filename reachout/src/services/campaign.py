from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from loguru import logger

from reachout.src.schemas.campaign import CampaignCreate
from reachout.src.models.campaign import Campaign, StatusEnum
from reachout.src.models.contact import Contact
from reachout.src.tasks.celery_app import celery_app


class CampaignService:
    def __init__(self, db: AsyncSession, redis_cli: Redis):
        self.db = db
        self.redis_cli = redis_cli


    async def add_task(self, payload: CampaignCreate, manager_id: int):
        logger.info(f"Менеджер #{manager_id} создает кампанию. Шаблон ID: {payload.template_id}, Целевой тег: '{payload.target_tag}'.")

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

        await self.redis_cli.delete(f"analytics:dashboard:{manager_id}")

        logger.success(f"Кампания ID: {new_campaign.id} успешно создана в статусе PENDING. Задача отправлена в очередь Celery.")
        return new_campaign


    async def get_all_campaigns(self, manager_id: int):
        logger.info(f"Менеджер #{manager_id} запросил все свои кампании.")

        query = select(Campaign).filter(Campaign.manager_id == manager_id)
        result = await self.db.execute(query)
        campaigns = result.scalars().all()

        if campaigns:
            logger.success(f"Успешно найдено {len(campaigns)}.")
        else:
            logger.info(f"Кампаний менеджера {manager_id} не найдено.")

        return campaigns


    async def get_campaign_by_id(self, campaign_id: int, manager_id: int):
        logger.info(f"Менеджер #{manager_id} запросил кампанию с id: {campaign_id}.")

        query = select(Campaign).filter(Campaign.id == campaign_id, Campaign.manager_id == manager_id)
        result = await self.db.execute(query)
        campaign = result.scalar_one_or_none()

        if campaign:
            logger.success(f"Кампания с id {campaign_id} успешно найдена.")
        else:
            logger.info(f"Кампания с id {campaign_id} не найдена.")

        return campaign