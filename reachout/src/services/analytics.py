import json
from redis.asyncio import Redis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from reachout.src.models.contact import Contact
from reachout.src.models.campaign import Campaign


class AnalyticService:
    def __init__(self, db: AsyncSession, redis_cli: Redis):
        self.db = db
        self.redis_cli = redis_cli


    async def get_manager_analytics(self, manager_id: int):
        cache_key = f"analytics:dashboard:{manager_id}"
        cached_data = await self.redis_cli.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        query = select(func.count(Contact.id)).filter(Contact.manager_id == manager_id)
        result = await self.db.execute(query)
        total_contacts = result.scalar_one_or_none()

        query = select(func.count(Campaign.id), func.sum(Campaign.total_recipients), func.sum(Campaign.sent_successfully)).filter(Campaign.manager_id == manager_id)
        result = await self.db.execute(query)
        campaign_data = result.fetchone()

        total_campaigns = campaign_data[0] or 0
        planed_letters = campaign_data[1] or 0
        sent_letters = campaign_data[2] or 0
        

        if planed_letters == 0:
            success_rate = 0.0
        else:
            success_rate = round(sent_letters / planed_letters * 100, 2)

        analytic_data = {"total_contacts": total_contacts, "total_campaigns": total_campaigns, "success_rate": success_rate}

        json_string = json.dumps(analytic_data)

        await self.redis_cli.set(
            cache_key,
            json_string,
            ex=300
        )

        return analytic_data