import pytest
from fastapi import status

def test_get_user_history(client, auth_headers, sample_query_log):
    """Test getting user query history"""
    response = client.get("/queries/history", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["question"] == sample_query_log.question
    assert data[0]["is_executable"] == sample_query_log.is_executable

def test_get_user_history_empty(client, auth_headers):
    """Test getting empty history"""
    response = client.get("/queries/history", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []

def test_get_user_history_unauthorized(client):
    """Test getting history without authentication"""
    response = client.get("/queries/history")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_query_by_id(client, auth_headers, sample_query_log):
    """Test getting specific query by ID"""
    response = client.get(f"/queries/{sample_query_log.id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_query_log.id
    assert data["question"] == sample_query_log.question

def test_delete_query(client, auth_headers, sample_query_log):
    """Test deleting a query"""
    response = client.delete(f"/queries/{sample_query_log.id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Consulta eliminada exitosamente"
    assert data["id"] == sample_query_log.id