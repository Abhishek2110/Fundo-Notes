import pytest
from rest_framework.reverse import reverse

# Create Note - Success
def test_create_note_should_return_success(db, client, login_fixture):
    note_data = {
        "title" : "Training Notes",
        "description" : "Sample Notes",
        "color" : "Green",
        "reminder": "2024-02-28T00:37:00Z"
    }
    url = reverse("NotesApi")
    response = client.post(url, note_data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {login_fixture}")
    assert response.status_code == 201
    
# Create Note - Failed
def test_create_note_should_return_failed(db, client, login_fixture):
    note_data = {
        "title" : "Training Notes",
        "description" : "Sample Notes",
        "color" : "Green",
        "reminder": "2024-02-28T00:37:00Z"
    }
    url = reverse("NotesApi")
    response = client.post(url, note_data, content_type="application/json")
    assert response.status_code == 401
    
# Get Note - Success
def test_read_note_should_return_success(db, client, create_note_fixture):
    url = reverse("NotesApi")
    response = client.get(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {create_note_fixture['token']}")
    assert response.status_code == 200

# Get Note - Failed
def test_read_note_should_return_failed(db, client, create_note_fixture):
    url = reverse("NotesApi")
    response = client.get(url, content_type="application/json")
    assert response.status_code == 401
    
# Update Note - Success
def test_update_note_should_return_success(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    token = create_note_fixture["token"]
    updated_note_data = {
        "id": note_id,
        "title" : "Training Notes 1",
        "description" : "Sample Notes 1",
        "color" : "Blue",
        "reminder": "2024-02-28T00:37:00Z"
    }
    url = reverse("NotesApi")
    response = client.put(url, updated_note_data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Update Note - Failed (Note not found)
def test_update_note_should_return_failed_note_not_found(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    token = create_note_fixture["token"]
    updated_note_data = {
        "title" : "Training Notes 1",
        "description" : "Sample Notes 1",
        "color" : "Blue",
        "reminder": "2024-02-28T00:37:00Z"
    }
    url = reverse("NotesApi")
    response = client.put(url, updated_note_data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 404
    
# Update Note - Failed (Authorization)
def test_update_note_should_return_failed_unauthorized(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    token = create_note_fixture["token"]
    updated_note_data = {
        "id": note_id,
        "title" : "Training Notes 1",
        "description" : "Sample Notes 1",
        "color" : "Blue",
        "reminder": "2024-02-28T00:37:00Z"
    }
    url = reverse("NotesApi")
    response = client.put(url, updated_note_data, content_type="application/json")
    assert response.status_code == 401
    
# Delete Note - Success
def test_delete_note_should_return_success(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    token = create_note_fixture["token"]
    url = reverse("NotesApi")
    url_with_query = f"{url}?id={note_id}"
    response = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Delete Note - Failed (Note not found)
def test_delete_note_should_return_failed_note_not_found(db, client, create_note_fixture):
    token = create_note_fixture["token"]
    url = reverse("NotesApi")
    response = client.delete(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 404
    
# Delete Note - Failed (Unauthorized)
def test_delete_note_should_return_failed_unauthorized(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    url = reverse("NotesApi")
    url_with_query = f"{url}?id={note_id}"
    response = client.delete(url_with_query, content_type="application/json")
    assert response.status_code == 401
    
# Archive Note (Patch) - Success
def test_archive_note_should_return_success(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    token = create_note_fixture["token"]
    url = reverse("ArchiveApi")
    url_with_query = f"{url}?note_id={note_id}"
    response = client.patch(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Archive Note (Patch) - Failed (Note not found)
def test_archive_note_should_return_failed_note_not_found(db, client, create_note_fixture):
    token = create_note_fixture["token"]
    url = reverse("ArchiveApi")
    url_with_query = f"{url}"
    response = client.patch(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 404
    
# Archive Note (Patch) - Failed (Unauthorized)
def test_archive_note_should_return_failed_unauthorized(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    url = reverse("ArchiveApi")
    url_with_query = f"{url}?note_id={note_id}"
    response = client.patch(url_with_query, content_type="application/json")
    assert response.status_code == 401
    
# Archive Note (Read) - Success 
def test_get_archive_note_should_return_success(db, client, create_note_fixture):
    token = create_note_fixture["token"]
    url = reverse("ArchiveApi")
    response = client.get(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Archive Note (Read) - Failed (Unauthorized)
def test_get_archive_note_should_return_failed(db, client, create_note_fixture):
    url = reverse("ArchiveApi")
    response = client.get(url, content_type="application/json")
    assert response.status_code == 401
    
# Trash Note (Patch) - Success
def test_trash_note_should_return_success(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    token = create_note_fixture["token"]
    url = reverse("TrashApi")
    url_with_query = f"{url}?note_id={note_id}"
    response = client.patch(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Trash Note (Patch) - Failed (Note not found)
def test_trash_note_should_return_failed_note_not_found(db, client, create_note_fixture):
    token = create_note_fixture["token"]
    url = reverse("TrashApi")
    url_with_query = f"{url}"
    response = client.patch(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 404
    
# Trash Note (Patch) - Failed (Unauthorized)
def test_trash_note_should_return_failed_unauthorized(db, client, create_note_fixture):
    note_id = create_note_fixture["note_id"]
    url = reverse("TrashApi")
    url_with_query = f"{url}?note_id={note_id}"
    response = client.patch(url_with_query, content_type="application/json")
    assert response.status_code == 401
    
# Trash Note (Get) - Success 
def test_get_trash_note_should_return_success(db, client, create_note_fixture):
    token = create_note_fixture["token"]
    url = reverse("TrashApi")
    response = client.get(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Trash Note (Get) - Failed (Unauthorized)
def test_get_trash_note_should_return_failed(db, client, create_note_fixture):
    url = reverse("TrashApi")
    response = client.get(url, content_type="application/json")
    assert response.status_code == 401
    
# Get one Note - Success
def test_get_one_note_should_return_success(db, client, create_note_fixture):
    token = create_note_fixture["token"]
    note_id = create_note_fixture["note_id"]
    url = reverse("NotesGetOneApi")
    url_with_query = f"{url}?id={note_id}"
    response = client.get(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Get one Note - Failed (Unauthorized)
def test_get_one_note_should_return_failed_unauthorized(db, client, create_note_fixture):
    url = reverse("NotesGetOneApi")
    url_with_query = f"{url}"
    response = client.get(url_with_query, content_type="application/json")
    assert response.status_code == 401
    
