from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.database.models import User
from src.database.db import get_db
from src.schemas import ContactRequest, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, db, user)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, db, user)
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactRequest, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}', response_model=ContactResponse)
async def update_contact(body: ContactRequest, contact_id: int,
                         db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    return contact


@router.delete('/{contact_id}', response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact


@router.get('/search', response_model=List[ContactResponse])
async def search_contacts(
        body: str = Query(..., description='Search contacts for name, last name or email'),
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    contacts = await repository_contacts.search_contacts(body, skip, limit, db, user)
    return contacts


@router.get('/birthdays/', response_model=List[ContactResponse])
async def upcoming_birthdays(db: Session = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    upcoming_birthdays_this_year = await repository_contacts.upcoming_birthdays(db, user)
    return upcoming_birthdays_this_year
