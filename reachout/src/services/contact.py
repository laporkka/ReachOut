from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from reachout.src.models.contact import Contact
from reachout.src.schemas.contact import ContactBulkUpload, ContactCreate


class ContactService:
    def __init__(self, db: AsyncSession, redis_cli: Redis):
        self.db = db
        self.redis_cli = redis_cli


    async def bulk_create_contacts(self, payload: ContactBulkUpload, manager_id: int) -> dict:
        list_of_emails: dict[str, ContactCreate] = {}

        for contact in payload.items:
            if contact.email not in list_of_emails:
                list_of_emails[contact.email] = contact

        query = select(Contact.email).filter(Contact.manager_id == manager_id, Contact.email.in_(list(list_of_emails.keys())))
        result = await self.db.execute(query)
        existing_emails = set(result.scalars().all())

        new_contacts = []

        for email, contact_data in list_of_emails.items():
            if email not in existing_emails:
                new_contact = Contact(
                    manager_id=manager_id,
                    first_name=contact_data.first_name,
                    email=contact_data.email,
                    birthday=contact_data.birthday,
                    tags=contact_data.tags
                )

                new_contacts.append(new_contact)
        
        self.db.add_all(new_contacts)
        await self.db.commit()

        total_incoming = len(payload.items)
        inserted_count = len(new_contacts)
        skipped_count = total_incoming - inserted_count

        await self.redis_cli.delete(f"analytics:dashboard:{manager_id}")
        
        return {"inserted": inserted_count, "skipped": skipped_count}