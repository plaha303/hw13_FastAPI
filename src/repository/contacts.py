from typing import Type
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactRequest


async def create_contact(body: ContactRequest, db: Session, user: User) -> Contact:
    if db.query(Contact).filter(
        and_(Contact.phone_number == body.phone_number, Contact.user_id == user.id)
    ).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Phone number already exists')
    db_contact = Contact(**body.model_dump(), user=user)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def get_contact(contact_id: int, db: Session, user: User) -> Type[Contact]:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact


async def get_contacts(skip: int, limit: int, db: Session, user: User) -> list[Type[Contact]]:
    contacts = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    return contacts


async def update_contact(contact_id: int,
                         updated_contact: ContactRequest,
                         db: Session,
                         user: User) -> Type[Contact]:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')

    for attr, value in updated_contact.model_dump().items():
        setattr(contact, attr, value)

    db.commit()
    db.refresh(contact)
    return contact


async def delete_contact(contact_id: int,
                         db: Session,
                         user: User) -> Type[Contact]:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    db.delete(contact)
    db.commit()
    return contact


async def search_contacts(
        body: str,
        skip: int,
        limit: int,
        db: Session,
        user: User
) -> list[Type[Contact]]:
    contacts = db.query(Contact).filter(and_(
        Contact.first_name.ilike(f'%{body}%')
        | Contact.last_name.ilike(f'%{body}%')
        | Contact.email.ilike(f'%{body}%'), Contact.user_id == user.id
    )).offset(skip).limit(limit).all()
    return contacts


async def upcoming_birthdays(db: Session,
                             user: User) -> list[Type[Contact]]:
    today = datetime.today()
    seven_days_after = today + timedelta(days=7)

    upcoming_birthdays_this_year = db.query(Contact).filter(and_(
        text("TO_CHAR(birthday, 'MM-DD') BETWEEN :start_date AND :end_date"),
        Contact.user_id == user.id
    )).params(start_date=today.strftime('%m-%d'), end_date=seven_days_after.strftime('%m-%d')).all()
    return upcoming_birthdays_this_year
