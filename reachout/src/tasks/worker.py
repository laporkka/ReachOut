from sqlalchemy import select
from loguru import logger

from reachout.src.core.database import SessionLocal
from reachout.src.tasks.celery_app import celery_app
from reachout.src.models.campaign import Campaign, StatusEnum
from reachout.src.models.contact import Contact
from reachout.src.models.campaign_log import Campaign_log


@celery_app.task(name="src.tasks.campaign_tasks.send_mass_email_task")
def send_mass_email_task(campaign_id: int):
    logger.info(f"Celery воркер принял задачу рассылки для кампании ID: {campaign_id}")

    with SessionLocal() as db:
        query = select(Campaign).filter(Campaign.id == campaign_id)
        result = db.execute(query)
        campaign = result.scalar_one_or_none()

        if not campaign:
            logger.error(f"Критическая ошибка Celery: Кампания ID: {campaign_id} не найдена в базе данных. Отмена задачи.")
            return

        campaign.status = StatusEnum.IN_PROGRESS
        
        db.commit()
        db.refresh(campaign)

        query = select(Contact).filter(Contact.manager_id == campaign.manager_id, Contact.tags.any(campaign.target_tag))
        result = db.execute(query)
        contacts = result.scalars().all()

        number_of_sents = 0
        for number_of_sents, contact in enumerate(contacts, start=1):
            letter: str = campaign.template.body
            personalized_letter = letter.format(first_name=contact.first_name)

            f"Кампания ID: {campaign_id} -> Имитация отправки email на адрес: {contact.email}, письмо: {personalized_letter}"

            new_log = Campaign_log(
                email=contact.email,
                campaign_id=campaign.id,
                template_id=campaign.template_id
            )

            db.add(new_log)

            if number_of_sents % 10 == 0:
                campaign.sent_successfully = number_of_sents
                db.commit()


        campaign.status = StatusEnum.SUCCESS
        campaign.sent_successfully = number_of_sents
        db.commit()

        f"Кампания ID: {campaign_id} успешно обработана воркером. Писем отправлено: {number_of_sents}. Статус изменен на SUCCESS. Отчет записан в campaign_logs."

