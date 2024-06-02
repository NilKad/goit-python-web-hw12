import logging
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Contact
from src.schemas.contact import ContactSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def search_contacts(filters: list, limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).filter_by(**filters).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_by_id(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def add_contact(body: ContactSchema, db: AsyncSession):
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        return None
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.phone = body.phone
    contact.email = body.email
    contact.birthday = body.birthday
    contact.addition = body.addition
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact is None:
        return None
    await db.delete(contact)
    await db.commit()
    return contact


async def next_birthday(bd_list: list[str], db: AsyncSession):
    stmt = select(Contact).filter(
        func.to_char(func.to_date(Contact.birthday, "YYYY-MM-DD"), "MM-DD").in_(bd_list)
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
