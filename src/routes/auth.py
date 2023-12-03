from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel,
                 background_tasks: BackgroundTasks,
                 request: Request,
                 db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
    It takes a UserModel object as input, which is validated by pydantic.
    The function also takes an instance of BackgroundTasks and Request from FastAPI,
    which are used to send an email to the user after they sign up.

    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the website
    :param db: Session: Get the database session
    :return: A dict with the user and a detail message
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {'user': new_user, 'detail': 'User successfully created. Check your email for confirmation.'}


@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes the username and password from the request body,
    verifies that they are correct, and returns an access token.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Access the database
    :return: A dict with the access token and refresh token
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')
    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database and if they have already confirmed their email.
        If not, then we update their record in our database with a confirmation of their email.

    :param token: str: Get the token from the url
    :param db: Session: Access the database
    :return: A message that the email is already confirmed
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    await repository_users.confirmed_email(email, db)
    return {'message': 'Email confirmed'}


@router.post('/request_email')
async def request_email(body: RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that they can click on
    to confirm their email address. The function takes in a RequestEmail object, which contains the
    email of the user who wants to confirm their account. It then checks if there is already a confirmed
    user with that email address, and if so returns an error message saying as much. If not, it sends
    an asynchronous task (using FastAPI's BackgroundTasks) to send_email(),
    passing in the user's email, username and base url.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
        return {'message': 'Check your email for confirmation.'}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns a new access_token, refresh_token pair.
    The function first decodes the given refresh token to get the email of its owner.
    Then it gets that user from our database and checks if their stored
    refresh_token matches with what was passed in as an argument (if not, we raise an error).
    If everything checks out, we create new tokens for this user using auth0's create functions.

    :param credentials: HTTPAuthorizationCredentials: Get the credentials from the request header
    :param db: Session: Get the database session
    :return: The access token and refresh token
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    access_token = await auth_service.create_access_token(data={'sub': email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}
