from datetime import timedelta

import bcrypt
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import dependencies, schemas, utils, crud, database
from api.settings import SETTINGS

app = FastAPI()


@app.on_event("startup")
def create_tables():
    database.Base.metadata.create_all(bind=database.engine)


##################################################
# USERS
##################################################

@app.post("/users", response_model=schemas.UserSafe)
async def register_user(
        user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(dependencies.get_db)
):
    existing_user = crud.user.get_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.user.create(db, user)
    verification_token = crud.verification_token.create(db, user_id=new_user.id)

    background_tasks.add_task(utils.send_verification_email, new_user.email, verification_token.token)

    return schemas.UserSafe.model_validate(new_user.dict())


@app.get("/users/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, db: Session = Depends(dependencies.get_db)):
    verification_token = crud.verification_token.get_by_token(db, token)
    if not verification_token:
        raise HTTPException(status_code=404, detail="Invalid verification token")

    user = crud.user.get_by_id(db, user_id=verification_token.user_id)

    verified = crud.user.verify(db, user.id)
    if not verified:
        raise HTTPException(status_code=500, detail="Error verifying email")

    crud.verification_token.delete_verification_token(db, token)

    return


@app.post("/users/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = crud.user.get_by_email(db, email=form_data.username)

    if not user or not bcrypt.checkpw(form_data.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/users/me", response_model=schemas.UserSafe)
async def get_current_user(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return schemas.UserSafe.model_validate(current_user.dict())

##################################################
# ENTITIES
##################################################


@app.post("/entities", response_model=schemas.Entity, dependencies=[Depends(dependencies.get_current_user)])
async def create_entity(
    entity: schemas.EntityCreate,
    db: Session = Depends(dependencies.get_db),
):
    shortened_url = utils.shorten_youtube_link(entity.url)

    existing_entity = crud.entity.get_by_url(db, url=shortened_url)
    if existing_entity:
        raise HTTPException(status_code=400, detail="Entity with this URL already exists")

    new_entity = crud.entity.create(db, entity)

    return new_entity


@app.get("/entities", response_model=schemas.EntityList)
async def search_entities(
    url: str,
    db: Session = Depends(dependencies.get_db),
):
    shortened_url = utils.shorten_youtube_link(url)

    entities = crud.entity.search_by_url(db, url=shortened_url)

    return schemas.EntityList(entities=entities)


@app.get("/entities/fetch", dependencies=[Depends(dependencies.get_current_user)])
async def fetch_entity_info(url: str):
    shortened_url = utils.shorten_youtube_link(url)

    entity_name = utils.get_open_graph_name(shortened_url)
    platform_name = utils.get_platform_name(shortened_url)

    return {
        "url": shortened_url,
        "name": entity_name,
        "platform": platform_name
    }


##################################################
# FEEDBACK
##################################################

@app.post("/feedbacks/{entity_id}", response_model=schemas.Feedback)
async def add_feedback(
    feedback_create: schemas.FeedbackCreateMin,
    entity_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user)
):
    entity = crud.entity.get_by_id(db, entity_id=entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    feedback_data = schemas.FeedbackCreate(text=feedback_create.text, user_id=current_user.id, entity_id=entity_id)
    new_feedback = crud.feedback.create(db, feedback=feedback_data)

    return new_feedback


@app.get("/feedbacks/entity/{entity_id}", dependencies=[Depends(dependencies.get_current_user)])
async def get_feedbacks(
    entity_id: int,
    sort_order: str = "asc",
    filter_last_days: int = None,
    db: Session = Depends(dependencies.get_db),
):
    entity = crud.entity.get_by_id(db, entity_id=entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    feedbacks = crud.feedback.get_by_entity_id(
        db, entity_id=entity_id, sort_order=sort_order, filter_last_days=filter_last_days
    )
    return schemas.FeedbackWithUsernameList(feedbacks=feedbacks)
