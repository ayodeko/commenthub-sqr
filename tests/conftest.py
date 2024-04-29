from datetime import timedelta

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import database, models, utils
from api.main import app
from api.dependencies import get_db
from api.settings import SETTINGS

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    database.Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

    database.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


@pytest.fixture(scope="function")
def test_user_not_verified(db_session):
    hashed_password = bcrypt.hashpw("securepassword".encode("utf-8"), bcrypt.gensalt())

    user = models.User(
        username="testuser",
        email="test@example.com",
        password=hashed_password.decode("utf-8")
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def test_user(db_session):
    hashed_password = bcrypt.hashpw("securepassword".encode("utf-8"), bcrypt.gensalt())

    user = models.User(
        username="testuser_verified",
        email="test1@example.com",
        password=hashed_password.decode("utf-8"),
        is_verified=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def test_user_token(test_user):
    access_token_expires = timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=access_token_expires,
    )
    return access_token