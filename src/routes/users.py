from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.config.config import settings
from src.schemas import UserDB

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me/', response_model=UserDB)
async def read_users_me(user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET endpoint that returns the current user's information.

    :param user: User: Specify the type of object that will be passed to the function
    :return: The current user object
    :doc-author: Trelent
    """
    return user


@router.patch('/avatar', response_model=UserDB)
async def update_avatar_user(file: UploadFile = File(),
                             user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function is used to update the avatar of a user.

    :param file: UploadFile: Upload the file to cloudinary
    :param user: User: Get the current user
    :param db: Session: Pass the database session to the repository layer
    :return: A user object
    :doc-author: Trelent
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'contacts/{user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'contacts/{user.username}')\
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(user.email, src_url, db)
    return user
