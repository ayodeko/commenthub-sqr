from fastapi import status

from api.schemas import EntityCreate


def test_create_entity(test_client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    entity_data = EntityCreate(
        name="Rick Astley - Never Gonna Give You Up (Official Music Video)",
        url="https://youtu.be/dQw4w9WgXcQ",
        platform="youtu.be"
    )

    response = test_client.post("/entities", headers=headers, json=entity_data.model_dump())
    assert response.status_code == status.HTTP_200_OK


def test_search_entities(test_client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    entity_data = EntityCreate(
        name="Rick Astley - Never Gonna Give You Up (Official Music Video)",
        url="https://youtu.be/dQw4w9WgXcQ",
        platform="youtu.be"
    )

    response = test_client.post("/entities", json=entity_data.model_dump(), headers=headers)
    assert response.status_code == status.HTTP_200_OK

    response = test_client.get("/entities", params={"url": entity_data.url})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["entities"]) > 0


def test_fetch_entity(test_client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}

    response = test_client.get("/entities/fetch", headers=headers, params={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["name"] == "Rick Astley - Never Gonna Give You Up (Official Music Video)"
    assert response_json["url"] == "https://youtu.be/dQw4w9WgXcQ"
    assert response_json["platform"] == "youtu.be"
