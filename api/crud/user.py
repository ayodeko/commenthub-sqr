from sqlalchemy.orm import Session
from api import models, schemas, utils


def create(db: Session, user: schemas.UserCreate):
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(**user.model_dump())
    db_user.password = hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.User.model_validate(db_user)


def get_by_id(db: Session, user_id: int) -> schemas.User | None:
    user = db.query(models.User).filter(models.User.id == user_id).first()  # type: ignore
    if user:
        return schemas.User.model_validate(user)
    return None


def get_by_email(db: Session, email: str) -> schemas.User | None:
    user = db.query(models.User).filter(models.User.email == email).first()  # type: ignore
    if user:
        return schemas.User.model_validate(user)
    return None


def verify(db: Session, user_id: int) -> bool:
    user = db.query(models.User).filter(models.User.id == user_id).first()  # type: ignore
    if not user:
        return False

    user.is_verified = True
    db.commit()
    db.refresh(user)
    return True
