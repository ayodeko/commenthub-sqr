from sqlalchemy.orm import Session
from api import models, schemas
import secrets


def create(db: Session, user_id: int) -> models.VerificationToken:
    token = secrets.token_hex(16)
    new_token = models.VerificationToken(
        token=token,
        user_id=user_id,
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return schemas.VerificationToken.model_validate(new_token)


def get_by_token(db: Session, token: str) -> models.VerificationToken | None:
    verification_token = (db.query(models.VerificationToken)
                          .filter(models.VerificationToken.token == token).first())  # type: ignore
    if verification_token:
        return schemas.VerificationToken.model_validate(verification_token)
    return None


def get_verification_token_by_user_id(db: Session, user_id: int) -> models.VerificationToken | None:
    verification_token = (db.query(models.VerificationToken)
                          .filter(models.VerificationToken.user_id == user_id).first())  # type: ignore
    if verification_token:
        return schemas.VerificationToken.model_validate(verification_token)
    return None


def delete_verification_token(db: Session, token: str) -> bool:
    verification_token = (db.query(models.VerificationToken)
                          .filter(models.VerificationToken.token == token).first())  # type: ignore
    if verification_token:
        db.delete(verification_token)
        db.commit()
        return True
    return False
