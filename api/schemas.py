from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr
    is_verified: bool

    class Config:
        from_attributes = True


class UserSafe(BaseModel):
    id: int
    username: str
    email: EmailStr


class VerificationToken(BaseModel):
    id: int
    token: str
    user_id: int

    class Config:
        from_attributes = True


class EntityCreate(BaseModel):
    url: str
    name: str
    platform: str


class Entity(BaseModel):
    id: int
    url: str
    name: str
    platform: str

    class Config:
        from_attributes = True


class EntityList(BaseModel):
    entities: list[Entity]


class FeedbackCreateMin(BaseModel):
    text: str


class FeedbackCreate(FeedbackCreateMin):
    user_id: int
    entity_id: int


class Feedback(BaseModel):
    id: int
    text: str
    created_at: datetime
    user_id: int
    entity_id: int

    class Config:
        from_attributes = True


class FeedbackWithUsername(Feedback):
    username: str


class FeedbackWithUsernameList(BaseModel):
    feedbacks: list[FeedbackWithUsername]
