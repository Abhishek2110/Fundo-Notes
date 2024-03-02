import pytest
from rest_framework.reverse import reverse

# Create Collaborators - Success
def test_create_collaborators_should_return_success(db, client, collaborator_fixture):
    token = collaborator_fixture["token"]
    note_id = collaborator_fixture["note_id"]
    user_id = collaborator_fixture["user_id"]
    collab_data = {
    "access_type": "read_write",
    "note": note_id,
    "collaborator": user_id
    }
    url = reverse("CollaboratorApi")
    response = client.post(url, collab_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 201
    
# Create Collaborators - Failed (Collaborator ID not provided)
def test_create_collaborators_should_return_failed_collab_id_not_provided(db, client, collaborator_fixture):
    token = collaborator_fixture["token"]
    note_id = collaborator_fixture["note_id"]
    user_id = collaborator_fixture["user_id"]
    collab_data = {
    "access_type": "read_write",
    "note": note_id,
    "collaborator": []
    }
    url = reverse("CollaboratorApi")
    response = client.post(url, collab_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Create Collaborators - Failed (Collaborator ID not provided)
def test_create_collaborators_should_return_failed_note_id_not_provided(db, client, collaborator_fixture):
    token = collaborator_fixture["token"]
    note_id = collaborator_fixture["note_id"]
    user_id = collaborator_fixture["user_id"]
    collab_data = {
    "access_type": "read_write",
    "collaborator": user_id
    }
    url = reverse("CollaboratorApi")
    response = client.post(url, collab_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Create Collaborators - Failed (Unauthorized)
def test_create_collaborators_should_return_failed_unauthorized(db, client, collaborator_fixture):
    note_id = collaborator_fixture["note_id"]
    user_id = collaborator_fixture["user_id"]
    collab_data = {
    "access_type": "read_write",
    "note": note_id,
    "collaborator": user_id
    }
    url = reverse("CollaboratorApi")
    response = client.post(url, collab_data, content_type="application/json")
    assert response.status_code == 401
    
# Delete Collaborators - Success
def test_delete_collaborators_should_return_success(db, client, collaborator_fixture):
    token = collaborator_fixture["token"]
    note_id = collaborator_fixture["note_id"]
    user_id = collaborator_fixture["user_id"]
    collab_data = {
    "access_type": "read_write",
    "note": note_id,
    "collaborator": user_id
    }
    url = reverse("CollaboratorApi")
    response = client.delete(url, collab_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Create Collaborators - Failed (Note ID not provided)
def test_delete_collaborators_should_return_failed_note_id_not_provided(db, client, collaborator_fixture):
    token = collaborator_fixture["token"]
    user_id = collaborator_fixture["user_id"]
    collab_data = {
    "access_type": "read_write",
    "collaborator": user_id
    }
    url = reverse("CollaboratorApi")
    response = client.post(url, collab_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Create Collaborators - Failed (Collaborator ID not provided)
def test_delete_collaborators_should_return_failed_collaborator_id_not_provided(db, client, collaborator_fixture):
    token = collaborator_fixture["token"]
    note_id = collaborator_fixture["note_id"]
    collab_data = {
    "access_type": "read_write",
    "note": note_id
    }
    url = reverse("CollaboratorApi")
    response = client.post(url, collab_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Delete Collaborators - Failed (Unauthorized)
def test_delete_collaborators_should_return_failed_unauthorized(db, client, collaborator_fixture):
    note_id = collaborator_fixture["note_id"]
    user_id = collaborator_fixture["user_id"]
    collab_data = {
    "access_type": "read_write",
    "note": note_id,
    "collaborator": user_id
    }
    url = reverse("CollaboratorApi")
    response = client.delete(url, collab_data, content_type="application/json")
    assert response.status_code == 401