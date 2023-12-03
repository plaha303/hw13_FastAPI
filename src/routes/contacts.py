from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.models import User
from src.database.db import get_db
from src.schemas import ContactRequest, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=List[ContactResponse],
            description='No more then 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))],
            status_code=status.HTTP_201_CREATED)
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):
    """
    The read_contacts function returns a list of contacts.

    :param skip: int: Skip a number of contacts from the database
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the repository
    :param user: User: Pass the user object to the function
    :return: The list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(skip, limit, db, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse,
            description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    The read_contact function is used to retrieve a single contact from the database.
    It takes in an integer representing the ID of the contact, and returns a Contact object.

    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the function
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    return contact


@router.post('/', response_model=List[ContactResponse],
             description='No more then 5 requests per minute',
             dependencies=[Depends(RateLimiter(times=5, seconds=60))],
             status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactRequest, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactRequest: Get the data from the request body
    :param db: Session: Pass the database session to the repository layer
    :param user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse,
            description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactRequest, contact_id: int,
                         db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes three arguments:
            - body: A ContactRequest object containing the new information for the contact.
            - contact_id: An integer representing the ID of an existing contact to be updated.
            - db (optional): A Session object used to connect to and query a database,
              if not provided, one will be created automatically using get_db().

    :param body: ContactRequest: Specify the type of data that will be passed in the request body
    :param contact_id: int: Specify the contact to be deleted
    :param db: Session: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse,
               description='No more than 10 request per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function deletes a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param user: User: Get the current user
    :return: The deleted contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact


@router.get("/search", response_model=List[ContactResponse],
            description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search_contacts(
        body: str = Query(..., description='Search contacts for name, last name or email'),
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    The search_contacts function is used to search for contacts in the database.
    It takes a string as an argument and searches for it in the name, last name or email fields of all contacts.
    The function returns a list of contact objects that match the query.

    :param body: str: Search for contacts by name, last name or email
    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of results returned
    :param db: Session: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.search_contacts(body, skip, limit, db, user)
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse],
            description='No more than 10 request per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upcoming_birthdays(db: Session = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    """
    The upcoming_birthdays function returns a list of contacts with upcoming birthdays.
    The function takes in the database session and the current user as parameters,
    and uses them to call the repository_contacts.upcoming_birthdays function.

    :param db: Session: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    upcoming_birthdays_this_year = await repository_contacts.upcoming_birthdays(db, user)
    return upcoming_birthdays_this_year
