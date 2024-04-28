from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from api.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)

    verification_tokens = relationship(
        "VerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    feedbacks = relationship(
        "Feedback",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="verification_tokens")


class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    platform = Column(String(50), nullable=False)

    feedbacks = relationship(
        "Feedback",
        back_populates="entity",
        cascade="all, delete-orphan",
    )


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey('users.id'))
    entity_id = Column(Integer, ForeignKey('entities.id'))

    user = relationship("User", back_populates="feedbacks")
    entity = relationship("Entity", back_populates="feedbacks")
