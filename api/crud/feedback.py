from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload
from api import models, schemas


def create(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return schemas.Feedback.model_validate(db_feedback)


def get_by_entity_id(
        db: Session, entity_id: int, sort_order: str = "asc", filter_last_days: int = None
) -> list[schemas.FeedbackWithUsername]:
    query = db.query(models.Feedback).filter(models.Feedback.entity_id == entity_id)  # type: ignore

    if filter_last_days:
        filter_date = datetime.utcnow() - timedelta(days=filter_last_days)
        query = query.filter(models.Feedback.created_at >= filter_date)

    if sort_order == "asc":
        query = query.order_by(models.Feedback.created_at.asc())
    else:
        query = query.order_by(models.Feedback.created_at.desc())

    query = query.options(joinedload(models.Feedback.user))

    feedbacks = []
    for feedback in query.all():
        feedbacks.append(schemas.FeedbackWithUsername.model_validate({
            "id": feedback.id,
            "text": feedback.text,
            "created_at": feedback.created_at,
            "user_id": feedback.user_id,
            "entity_id": feedback.entity_id,
            "username": feedback.user.username
        }))

    return feedbacks
