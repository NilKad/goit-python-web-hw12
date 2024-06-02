from datetime import datetime, timedelta
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.contact import (
    ContactResponse,
    ContactSchema,
)
from src.database.db import get_db


from src.repositories import contacts as repositories_contact

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/search", response_model=list[ContactResponse])
async def search_contacts(
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    filters = {}
    if first_name:
        filters["first_name"] = first_name
    if last_name:
        filters["last_name"] = last_name
    if email:
        filters["email"] = email

    contacts = await repositories_contact.search_contacts(filters, limit, offset, db)
    print(f"return from function {contacts=}")
    return contacts


# search_contacts_next_birthday
@router.get("/next_birthday", response_model=list[ContactResponse])
async def next_birthday(next_day: int = 7, db: AsyncSession = Depends(get_db)):
    bd_list = []
    for i in range(next_day):
        date_search = datetime.now().date() + timedelta(days=i)
        date_search = datetime.strftime(date_search, "%m-%d")
        bd_list.append(date_search)
    contacts = await repositories_contact.next_birthday(bd_list, db)
    return contacts


@router.get("/{contact_id}", response_model=Optional[ContactResponse])
async def get_contact_by_id(
    contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)
):
    contact = await repositories_contact.get_contact_by_id(contact_id, db)
    if contact is None:
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     # status_code=400,
        #     detail=f"Contact with id {contact_id} not found",
        # )
        # return None
        return JSONResponse(status_code=404, content={"detail": "Contact not found"})
    return contact


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    contacts = await repositories_contact.get_contacts(limit, offset, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def add_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contact.add_contact(body, db)
    return contact


@router.put("/{contact_id}", response_model=Optional[ContactResponse])
async def update_contact(
    body: ContactSchema,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
):
    contact = await repositories_contact.update_contact(contact_id, body, db)
    if contact is None:
        return JSONResponse(status_code=404, content={"detail": "Contact not found"})
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)
):
    contact = await repositories_contact.delete_contact(contact_id, db)
    return contact
