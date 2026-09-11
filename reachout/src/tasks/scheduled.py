from celery import shared_task
from sqlalchemy import select
from datetime import datetime, timezone
from collections import defaultdict

from reachout.src.core.database import SessionLocal
from reachout.src.models.contact import Contact
from reachout.src.models.template import Template
from reachout.src.models.campaign import Campaign, StatusEnum
from reachout.src.tasks.celery_app import celery_app


@celery_app.task(name="src.tasks.scheduled.check_birthdays_task")
def check_birthdays_task():
    today_date = datetime.now(timezone.utc).strftime("%m-%d")

    with SessionLocal() as db:
        query = select(Contact).filter(Contact.birthday.like(f"%{today_date}"))
        result = db.execute(query)
        contacts = result.scalars().all()

        if not contacts:
            return
        
        manager_contacts = defaultdict(list)

        for contact in contacts:
            manager_contacts[contact.manager_id].append(contact)

        for manager_id, clients in manager_contacts.items():
            query = select(Template).filter(Template.manager_id == manager_id, Template.title == "Birthday")
            result = db.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                continue

            new_campaign = Campaign(
                manager_id=manager_id,
                template_id=template.id,
                target_tag="Auto-Birthday",
                status=StatusEnum.PENDING,
                total_recipients=len(clients)
            )

            db.add(new_campaign)
            db.commit()
            db.refresh(new_campaign)        

            celery_app.send_task(
                "src.tasks.campaign_tasks.send_mass_email_task",
                kwargs={"campaign_id": new_campaign.id}
            )
