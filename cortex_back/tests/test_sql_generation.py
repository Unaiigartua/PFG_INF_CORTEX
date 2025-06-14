import pytest
from unittest.mock import patch

def test_sql_generation_success(client, auth_headers):
    """Test successful SQL generation"""
    request_data = {
        "question": "How many patients have diabetes?",
        "medical_terms": [
            {"term": "diabetes", "concept_id": "201826"}
        ]
    }
    
    mock_response = {
        "question": request_data["question"],
        "generated_sql": "SELECT COUNT(*) FROM person p JOIN condition_occurrence co ON p.person_id = co.person_id WHERE co.condition_concept_id = 201826;",
        "is_executable": True,
        "attempts_count": 1,
        "error_message": None,
        "similar_example": None
    }
    
    with patch('app.sql_generation.service.SQLGenerationService.generate_sql', return_value=type('MockResponse', (), mock_response)()):
        response = client.post("/sql-generation/", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == request_data["question"]
        assert data["is_executable"] is True
        assert "SELECT COUNT(*)" in data["generated_sql"]

def test_sql_generation_unauthorized(client):
    """Test SQL generation without authentication"""
    request_data = {
        "question": "How many patients have diabetes?",
        "medical_terms": []
    }
    
    response = client.post("/sql-generation/", json=request_data)
    
    assert response.status_code == 401

def test_sql_generation_health_check(client):
    """Test SQL generation health check"""
    with patch('app.sql_generation.service.SQLGenerationService') as mock_service:
        mock_service.return_value.model_name = "test-model"
        
        response = client.get("/sql-generation/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sql_generation"
