from datetime import date, datetime

from pydantic import BaseModel, Field


class ContactRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=25)


class UserDB(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDB
    detail: str = 'User successfully created'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
