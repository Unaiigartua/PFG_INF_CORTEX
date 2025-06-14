import pytest
from unittest.mock import patch

def test_similar_terms_db_success(client, mock_similar_terms):
    """Test successful similar terms lookup with mock"""
    with patch('app.medical.similarity_bd.get_similar_terms_bd', return_value=mock_similar_terms):
        response = client.post("/similar_db", json={"term": "diabetes"})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) >= 1
        assert data["results"][0]["term"] == "diabetes mellitus"
        assert data["results"][0]["concept_id"] == "201820"

def test_similar_terms_db_real_service(client):
    """Test similar terms with real service (no mocks)"""
    response = client.post("/similar_db", json={"term": "diabetes"})
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    # El servicio real debería devolver múltiples resultados
    assert len(data["results"]) > 0
    # Verificar que al menos uno de los resultados está relacionado con diabetes
    diabetes_found = any("diabetes" in result["term"].lower() or 
                        "diabetes" in result["preferred_term"].lower() 
                        for result in data["results"])
    assert diabetes_found

def test_similar_terms_db_no_results(client):
    """Test similar terms with very specific unknown term"""
    with patch('app.medical.similarity_bd.get_similar_terms_bd', return_value=[]):
        response = client.post("/similar_db", json={"term": "unknownmedicalterm12345"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["results"] != []

def test_similarity_health_endpoint(client):
    """Test similarity service health check"""
    response = client.get("/similarity/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "medical_similarity"
    assert "stats" in data

def test_similarity_service_handles_edge_cases(client):
    """Test similarity service with edge cases"""
    # Test con texto muy corto
    response = client.post("/similar_db", json={"term": "a"})
    assert response.status_code == 200
    
    # Test con texto muy largo
    long_term = "very long medical term that probably does not exist in the database" * 10
    response = client.post("/similar_db", json={"term": long_term})
    assert response.status_code == 200
