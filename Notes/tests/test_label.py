import pytest
from rest_framework.reverse import reverse

# Create Label - Success
# @pytest.mark.abc
def test_create_label_should_return_success(db, client, login_fixture):
    label_data = {
        "name": "MN"
    }
    url = reverse("LabelApi")
    response = client.post(url, label_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {login_fixture}")
    print(response.data)
    assert response.status_code == 201
    
# Create Label - Failed 
def test_create_label_should_return_failed(db, client, login_fixture):
    label_data = {
    }
    url = reverse("LabelApi")
    response = client.post(url, label_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {login_fixture}")
    assert response.status_code == 400

# Create Label - Failed (Unauthorized)    
def test_create_label_should_return_failed_unauthorized(db, client, login_fixture):
    label_data = {
    "name": "MN"
    }
    url = reverse("LabelApi")
    response = client.post(url, label_data, content_type="application/json")
    assert response.status_code == 401 
  
# Get Label - Success  
def test_get_label_should_return_success(db, client, create_label_fixture):
    token = create_label_fixture["token"]
    url = reverse("LabelApi")
    response = client.get(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200

# Get Label - Failed (Unauthorized) 
def test_get_label_should_return_failed(db, client, create_label_fixture):
    url = reverse("LabelApi")
    response = client.get(url, content_type="application/json")
    assert response.status_code == 401
    
# Update Label - Success  
def test_update_label_should_return_success(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    updated_label_data = {
    "id": id,
    "name": "ML"
    }
    url = reverse("LabelApi")
    response = client.put(url, updated_label_data, content_type="application/json",HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Update Label - Failed (Label does not exist)  
def test_update_label_should_return_failed_label_not_found(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    updated_label_data = {
    "id": 15,
    "name": "ML"
    }
    url = reverse("LabelApi")
    response = client.put(url, updated_label_data, content_type="application/json",HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 404
    
# Update Label - Failed (Label ID not provided)
def test_update_label_should_return_failed_label_id_not_provided(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    updated_label_data = {
    "name": "ML"
    }
    url = reverse("LabelApi")
    response = client.put(url, updated_label_data, content_type="application/json",HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
 
# Update Label - Failed (Name not provided)   
def test_update_label_should_return_failed_name_not_provided(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    updated_label_data = {
    "id": id
    }
    url = reverse("LabelApi")
    response = client.put(url, updated_label_data, content_type="application/json",HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Update Label - Failed (Unauthorized)
def test_update_label_should_return_failed_unauthorized(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    updated_label_data = {
    "id": id,
    "name": "ML"
    }
    url = reverse("LabelApi")
    response = client.put(url, updated_label_data, content_type="application/json")
    assert response.status_code == 401
    
# Delete Label - Success
def test_delete_label_should_return_success(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    url = reverse("LabelApi")
    url_with_query = f"{url}?id={id}"
    response = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Delete Label - Failed (Label ID not provided)
def test_delete_label_should_return_failed_id_not_provided(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    url = reverse("LabelApi")
    url_with_query = f"{url}?id={id}"
    response = client.delete(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Delete Label - Failed (Label not found)
def test_delete_label_should_return_failed_label_not_found(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    url = reverse("LabelApi")
    url_with_query = f"{url}?id={id}"
    response = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    response1 = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response1.status_code == 404
    
# Delete Label - Failed (Label does not exist)
def test_delete_label_should_return_failed_label_does_not_exist(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    url = reverse("LabelApi")
    url_with_query = f"{url}?id={2}"
    response = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 404
    
# Delete Label - Failed (Unauthorized)
def test_delete_label_should_return_failed_unauthorized(db, client, create_label_fixture):
    id = create_label_fixture["id"]
    token = create_label_fixture["token"]
    url = reverse("LabelApi")
    url_with_query = f"{url}?id={id}"
    response = client.delete(url_with_query, content_type="application/json")
    assert response.status_code == 401