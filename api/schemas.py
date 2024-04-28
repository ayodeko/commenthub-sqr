from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    password: str
    email: EmailStr
    is_verified: bool


class UserSafe(BaseModel):
    id: int
    username: str
    email: EmailStr


class VerificationToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token: str
    user_id: int


class EntityCreate(BaseModel):
    url: str
    name: str
    platform: str


class Entity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    name: str
    platform: str


class EntityList(BaseModel):
    entities: list[Entity]


class FeedbackCreateMin(BaseModel):
    text: str


class FeedbackCreate(FeedbackCreateMin):
    user_id: int
    entity_id: int


class Feedback(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
    user_id: int
    entity_id: int


class FeedbackWithUsername(Feedback):
    username: str


class FeedbackWithUsernameList(BaseModel):
    feedbacks: list[FeedbackWithUsername]
