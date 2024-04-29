from fastapi import status, BackgroundTasks

from api import models
from api.schemas import UserCreate


def test_register_user(test_client, db_session, mocker):
    spy = mocker.spy(BackgroundTasks, "add_task")

    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )

    response = test_client.post("/users", json=user_data.model_dump())
    assert response.status_code == status.HTTP_200_OK

    spy.assert_called_once()

    response = test_client.post("/users", json=user_data.model_dump())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_verify_email(test_client, db_session):
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )
    response = test_client.post("/users", json=user_data.model_dump())
    user = response.json()

    token = db_session.query(models.VerificationToken).filter_by(user_id=user['id']).first()

    response = test_client.get(f"/users/verify/{token.token}")
    assert response.status_code == status.HTTP_200_OK

    response = test_client.get("/users/verify/invalid_token")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_login_user(test_client, db_session):
    # Register a user to log in
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )
    test_client.post("/users", json=user_data.model_dump())

    response = test_client.post(
        "/users/login", data={"username": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

    response = test_client.post(
        "/users/login", data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(test_client, db_session, test_user, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    user_response = test_client.get("/users/me", headers=headers)

    assert user_response.status_code == status.HTTP_200_OK

    assert "email" in user_response.json()
    assert user_response.json()["email"] == test_user.email

    assert "username" in user_response.json()
    assert user_response.json()["username"] == test_user.username
