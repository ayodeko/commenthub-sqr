from sqlalchemy.orm import Session
from api import models, schemas


def create(db: Session, entity: schemas.EntityCreate):
    db_entity = models.Entity(**entity.model_dump())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return schemas.Entity.model_validate(db_entity)


def get_by_id(db: Session, entity_id: int) -> schemas.Entity | None:
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()  # type: ignore
    if entity:
        return schemas.Entity.model_validate(entity)
    return None


def get_by_url(db: Session, url: str) -> schemas.Entity | None:
    entity = db.query(models.Entity).filter(models.Entity.url == url).first()  # type: ignore
    if entity:
        return schemas.Entity.model_validate(entity)
    return None


def search_by_url(db: Session, url: str) -> list[schemas.Entity]:
    entities_db = db.query(models.Entity).filter(models.Entity.url.contains(url)).all()
    entities = []
    for entity in entities_db:
        entities.append(schemas.Entity.model_validate(entity))
    return entities
