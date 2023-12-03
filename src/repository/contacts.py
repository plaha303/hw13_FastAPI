from typing import Type
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactRequest


async def create_contact(body: ContactRequest, db: Session, user: User) -> Contact:
    """
    The create_contact function creates a new contact in the database.
        It takes a ContactRequest object as input, which is validated by pydantic.
        The function then checks if the phone number already exists for that user, and returns an error if it does.
        If not, it adds the contact to the database and returns it.

    :param body: ContactRequest: Specify the type of data that is expected in the request body
    :param db: Session: Access the database
    :param user: User: Get the user_id from the jwt token
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The get_contact function takes a contact_id and returns the corresponding Contact object.
    If no such contact exists, it raises an HTTPException with status code 404.

    :param contact_id: int: Get the contact id from the path parameter
    :param db: Session: Access the database
    :param user: User: Check if the user is authorized to access this contact
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact


async def get_contacts(skip: int, limit: int, db: Session, user: User) -> list[Type[Contact]]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: int: Skip the first x number of contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user's contacts
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    return contacts


async def update_contact(contact_id: int,
                         updated_contact: ContactRequest,
                         db: Session,
                         user: User) -> Type[Contact]:
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Identify the contact to be deleted
    :param updated_contact: ContactRequest: Pass in the updated contact information
    :param db: Session: Access the database
    :param user: User: Get the user_id of the contact
    :return: The updated contact
    :doc-author: Trelent
    """
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
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (Session): A connection to the database.
            user (User): The user who is making this request, used for authorization purposes.

    :param contact_id: int: Specify the id of the contact that we want to delete
    :param db: Session: Access the database
    :param user: User: Get the user id from the token and use it to filter contacts
    :return: The deleted contact
    :doc-author: Trelent
    """
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
    """
    The search_contacts function searches for contacts in the database.
        Args:
            body (str): The search query string.
            skip (int): Number of records to skip for pagination. Default is 0.
            limit (int): Maximum number of records to return. Default is 100, upper limit is 1000, lower limit is 1.

    :param body: str: Search the database for contacts that match
    :param skip: int: Skip the first n contacts in the list
    :param limit: int: Limit the number of results returned
    :param db: Session: Access the database
    :param user: User: Get the user id from the token
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(and_(
        Contact.first_name.ilike(f'%{body}%')
        | Contact.last_name.ilike(f'%{body}%')
        | Contact.email.ilike(f'%{body}%'), Contact.user_id == user.id
    )).offset(skip).limit(limit).all()
    return contacts


async def upcoming_birthdays(db: Session,
                             user: User) -> list[Type[Contact]]:
    """
    The upcoming_birthdays function returns a list of contacts whose birthdays are within the next seven days.
        Args:
            db (Session): The database session to use for querying.
            user (User): The user who's contacts we want to query for upcoming birthdays.

    :param db: Session: Access the database
    :param user: User: Identify the user who is making the request
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    today = datetime.today()
    seven_days_after = today + timedelta(days=7)

    upcoming_birthdays_this_year = db.query(Contact).filter(and_(
        text("TO_CHAR(birthday, 'MM-DD') BETWEEN :start_date AND :end_date"),
        Contact.user_id == user.id
    )).params(start_date=today.strftime('%m-%d'), end_date=seven_days_after.strftime('%m-%d')).all()
    return upcoming_birthdays_this_year
