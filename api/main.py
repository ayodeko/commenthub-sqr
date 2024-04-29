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


@app.head("/healthcheck")
async def healthcheck():
    """
    Check if the server is up and running.

    Returns:
    - dict: A dictionary containing the status of the server.
    """
    return {"status": "ok"}


##################################################
# USERS
##################################################

@app.post("/users", response_model=schemas.UserSafe)
async def register_user(
        user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(dependencies.get_db)
):
    """
    Register a new user.

    Parameters:
    - user (schemas.UserCreate): The user object containing email and password.

    Returns:
    - schemas.UserSafe: A safe version (without password) of the newly created user object.

    Raises:
    - HTTPException: If the email is already registered.
    """
    existing_user = crud.user.get_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.user.create(db, user)
    verification_token = crud.verification_token.create(db, user_id=new_user.id)

    background_tasks.add_task(utils.send_verification_email, new_user.email, verification_token.token)

    return schemas.UserSafe.model_validate(new_user.model_dump())


@app.get("/users/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, db: Session = Depends(dependencies.get_db)):
    """
    Verify the user's email address.

    Parameters:
    - token (str): The token generated during the registration process.

    Returns:
    - None: This endpoint does not return any data. It only verifies the user's email address.

    Raises:
    - HTTPException: If the verification token is invalid or has already been used.
    """
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
    """
    Logs in a user by validating their email and password.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): The form data containing the user's email and password.

    Returns:
    - dict: A dictionary containing the access token and token type.

    Raises:
    - HTTPException: If the email or password is invalid.
    """
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
    """
    Retrieve info for currently logged-in user.

    Returns:
    - schemas.UserSafe: User info.

    Raises:
    - HTTPException: If user is not logged in.
    """
    return schemas.UserSafe.model_validate(current_user.model_dump())

##################################################
# ENTITIES
##################################################


@app.post("/entities", response_model=schemas.Entity, dependencies=[Depends(dependencies.get_current_user)])
async def create_entity(
    entity: schemas.EntityCreate,
    db: Session = Depends(dependencies.get_db),
):
    """
    Create a new entity.

    Parameters:
    - entity (schemas.EntityCreate): The entity object containing the URL.

    Returns:
    - schemas.Entity: A newly created entity object.

    Raises:
    - HTTPException: If an entity with the same URL already exists.
    """
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
    """
    Search for entities by URL.

    Parameters:
    - url (str): The URL to search for entities.

    Returns:
    - schemas.EntityList: A list of entities matching the provided URL.

    Raises:
    - HTTPException: If an entity with the same URL already exists.
    """
    shortened_url = utils.shorten_youtube_link(url)

    entities = crud.entity.search_by_url(db, url=shortened_url)

    return schemas.EntityList(entities=entities)


@app.get("/entities/fetch", dependencies=[Depends(dependencies.get_current_user)])
async def fetch_entity_info(url: str):
    """
    Fetch information about an entity from its URL.

    Parameters:
    - url (str): The URL of the entity to fetch information about.

    Returns:
    - dict: A dictionary containing the URL, entity name, and platform name of the entity.

    Raises:
    - HTTPException: If the entity with the given URL does not exist.
    """
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
    """
    Add a new feedback to an entity.

    Parameters:
    - feedback_create (schemas.FeedbackCreateMin): The feedback object containing the text and user ID.
    - entity_id (int): The ID of the entity to which the feedback is being added.

    Returns:
    - schemas.Feedback: A newly created feedback object.

    Raises:
    - HTTPException: If the entity with the given ID does not exist.
    """
    entity = crud.entity.get_by_id(db, entity_id=entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    feedback_data = schemas.FeedbackCreate(text=feedback_create.text, user_id=current_user.id, entity_id=entity_id)
    new_feedback = crud.feedback.create(db, feedback=feedback_data)

    return new_feedback


@app.get("/feedbacks/{entity_id}")
async def get_feedbacks(
    entity_id: int,
    sort_order: str = "asc",
    filter_last_days: int = None,
    db: Session = Depends(dependencies.get_db),
):
    """
    Retrieve feedbacks for a specific entity.

    Parameters:
    - entity_id (int): The ID of the entity to retrieve feedbacks for.
    - sort_order (str): The order in which to sort the feedbacks. Defaults to "asc" (ascending).
    - filter_last_days (int): The number of days to filter feedbacks by. Defaults to None.

    Returns:
    - schemas.FeedbackWithUsernameList: A list of feedbacks for the specified entity, along with the username of
                                        the user who provided the feedback.

    Raises:
    - HTTPException: If the entity with the given ID does not exist.
    """
    entity = crud.entity.get_by_id(db, entity_id=entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    feedbacks = crud.feedback.get_by_entity_id(
        db, entity_id=entity_id, sort_order=sort_order, filter_last_days=filter_last_days
    )
    return schemas.FeedbackWithUsernameList(feedbacks=feedbacks)
