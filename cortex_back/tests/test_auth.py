import pytest
from fastapi import status

def test_register_user(client):
    """Test user registration"""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123"
    }
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert data["is_active"] is True

def test_register_duplicate_email(client, test_user):
    """Test registration with existing email fails"""
    user_data = {
        "email": test_user.email,
        "password": "password123"
    }
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email ya registrado" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test successful login"""
    login_data = {
        "username": test_user.email,
        "password": "testpassword123"
    }
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_user):
    """Test login with wrong password"""
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciales inválidas" in response.json()["detail"]

def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_auth_workflow_complete(client):
    """Test complete authentication workflow"""
    # Register
    user_data = {"email": "workflow@test.com", "password": "workflow123"}
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200
    
    # Login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Use token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == user_data["email"]