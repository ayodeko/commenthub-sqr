from fastapi import status

from api.schemas import FeedbackCreateMin, EntityCreate


def test_add_feedback(test_client, test_user_token, test_user):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    feedback_data = FeedbackCreateMin(
        text="Great content!"
    )

    entity_data = EntityCreate(
        name="Rick Astley - Never Gonna Give You Up (Official Music Video)",
        url="https://youtu.be/dQw4w9WgXcQ",
        platform="youtu.be"
    )
    entity_response = test_client.post("/entities", json=entity_data.model_dump(), headers=headers)
    entity = entity_response.json()

    response = test_client.post(
        f"/feedbacks/{entity['id']}", headers=headers, json=feedback_data.model_dump()
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    assert response_json["text"] == feedback_data.text
    assert response_json["user_id"] == test_user.id
    assert response_json["entity_id"] == entity["id"]


def test_get_feedbacks(test_client, test_user_token, test_user):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    entity_data = EntityCreate(
        name="Rick Astley - Never Gonna Give You Up (Official Music Video)",
        url="https://youtu.be/dQw4w9WgXcQ",
        platform="youtu.be"
    )
    entity_response = test_client.post("/entities", json=entity_data.model_dump(), headers=headers)
    entity = entity_response.json()

    feedback_data = FeedbackCreateMin(
        text="Great content!"
    )
    test_client.post(
        f"/feedbacks/{entity['id']}", headers=headers, json=feedback_data.model_dump()
    )

    response = test_client.get(f"/feedbacks/{entity['id']}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json["feedbacks"]) == 1
    response_feedback = response_json["feedbacks"][0]
    assert response_feedback["text"] == feedback_data.text
    assert response_feedback["user_id"] == test_user.id
    assert response_feedback["entity_id"] == entity["id"]
    assert response_feedback["username"] == test_user.username
