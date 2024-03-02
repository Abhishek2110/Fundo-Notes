import pytest
from rest_framework.reverse import reverse

@pytest.fixture
@pytest.mark.django_db
def login_fixture(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    
    login_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234"
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    # note_id = response_note.data["data"]["id"]
    # print(response_note.data)
    return response.data['token']

@pytest.fixture
@pytest.mark.django_db
def create_note_fixture(client, login_fixture):
    note_data = {
        "title": "Training Notes",
        "description": "Sample Notes",
        "color": "Green",
        "reminder": "2024-02-28T00:37:00Z"
    }
    url = reverse("NotesApi")
    response = client.post(url, note_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {login_fixture}")
    return {'token': login_fixture, 'note_id': response.data["data"]["id"]}
    
@pytest.fixture
@pytest.mark.django_db
def create_label_fixture(client, login_fixture):
    label_data = {
    "name": "MN"
    }
    url = reverse("LabelApi")
    response = client.post(url, label_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {login_fixture}")
    return {'token': login_fixture, 'id': response.data["data"]["id"]}
    
@pytest.fixture
@pytest.mark.django_db
def collaborator_fixture(client):
    register_data_user1 = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data_user1, content_type="application/json")
    
    register_data_user2 = {
        "username" : "Abhishek",
        "password" : "Abhishek@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("userApi")
    response_user2 = client.post(url, register_data_user2, content_type="application/json")
    print(response.data)
    
    login_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234"
    }
    url = reverse("login")
    response_token = client.post(url, login_data, content_type="application/json")

    note_data = {
        "title": "Training Notes",
        "description": "Sample Notes",
        "color": "Green",
        "reminder": "2024-02-28T00:37:00Z"
    }
    url = reverse("NotesApi")
    response_note = client.post(url, note_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {response_token.data['token']}")
    note_id = response_note.data["data"]["id"]
    user_id = []
    user_id.append(response_user2.data["data"]["id"])
    # print(response_note.data)
    return {"token": response_token.data['token'], "note_id": note_id, "user_id": user_id}