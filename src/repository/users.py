from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it will return None.

    :param email: str: Pass in the email address of the user we want to retrieve
    :param db: Session: Connect to the database
    :return: The first user in the database that matches the email provided
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        Args:
            body (UserModel): The UserModel object to be created.
            db (Session): The SQLAlchemy session object used for querying the database.

    :param body: UserModel: Validate the data that is passed into the function
    :param db: Session: Access the database
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user in the database
    :param token: str | None: Update the refresh token in the database
    :param db: Session: Commit the changes to the database
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: str: Find the user in the database
    :param url: str: Update the avatar url of a user
    :param db: Session: Access the database
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
