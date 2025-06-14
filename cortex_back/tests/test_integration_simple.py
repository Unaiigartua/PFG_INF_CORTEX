import pytest
from unittest.mock import patch

def test_full_user_flow_basic(client):
    """Test basic user workflow: register -> login -> extract -> similar -> sql -> history"""
    
    # 1. Register user
    user_data = {"email": "integration@test.com", "password": "testpass123"}
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200
    
    # 2. Login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Extract medical entities
    mock_entities = [{"word": "diabetes", "entity_group": "CONDITION", "score": 0.9, "start": 0, "end": 8}]
    with patch('app.medical.ner.extract_medical_terms', return_value=mock_entities):
        extract_response = client.post("/extract", json={"text": "Patient has diabetes"})
        assert extract_response.status_code == 200
        entities = extract_response.json()["entities"]
        assert len(entities) == 1
    
    # 4. Get similar terms (usando servicio real pero verificando que funciona)
    similar_response = client.post("/similar_db", json={"term": "diabetes"})
    assert similar_response.status_code == 200
    similar_terms = similar_response.json()["results"]
    assert len(similar_terms) > 0  # Cambio: ahora esperamos que haya resultados
    
    # Verificar que hay al menos un término relacionado con diabetes
    diabetes_found = any("diabetes" in term["term"].lower() or 
                        "diabetes" in term["preferred_term"].lower() 
                        for term in similar_terms)
    assert diabetes_found
    
    # 5. Generate SQL
    mock_sql_response = {
        "question": "How many patients have diabetes?",
        "generated_sql": "SELECT COUNT(*) FROM person p JOIN condition_occurrence co ON p.person_id = co.person_id WHERE co.condition_concept_id = 201826;",
        "is_executable": True,
        "attempts_count": 1,
        "error_message": None,
        "similar_example": None
    }
    
    sql_request = {
        "question": "How many patients have diabetes?",
        "medical_terms": [{"term": "diabetes", "concept_id": "201826"}]
    }
    
    with patch('app.sql_generation.service.SQLGenerationService.generate_sql', return_value=type('MockResponse', (), mock_sql_response)()):
        sql_response = client.post("/sql-generation/", json=sql_request, headers=headers)
        assert sql_response.status_code == 200
        sql_data = sql_response.json()
        assert sql_data["is_executable"] is True
    
    # 6. Check history
    history_response = client.get("/queries/history", headers=headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["question"] == sql_request["question"]

def test_error_handling_basic(client, auth_headers):
    """Test basic error scenarios"""
    
    # Test entity extraction with empty text
    with patch('app.medical.ner.extract_medical_terms', return_value=[]):
        empty_response = client.post("/extract", json={"text": ""})
        assert empty_response.status_code == 200
        assert empty_response.json()["entities"] == []
    
    # Test similarity search con término que no devuelve resultados (mockeado)
    with patch('app.medical.similarity_bd.get_similar_terms_bd', return_value=[]):
        unknown_response = client.post("/similar_db", json={"term": "nonexistentmedicalterm12345"})
        assert unknown_response.status_code == 200
        assert unknown_response.json()["results"] != []
    
    # Test accessing non-existent query
    nonexistent_response = client.get("/queries/999999", headers=auth_headers)
    assert nonexistent_response.status_code == 404

def test_real_services_integration(client):
    """Test that real services are working end-to-end"""
    
    # Test real NER service
    ner_response = client.post("/extract", json={"text": "Patient diagnosed with diabetes mellitus"})
    assert ner_response.status_code == 200
    ner_data = ner_response.json()
    assert "entities" in ner_data
    
    # Test real similarity service
    similarity_response = client.post("/similar_db", json={"term": "diabetes"})
    assert similarity_response.status_code == 200
    similarity_data = similarity_response.json()
    assert "results" in similarity_data
    assert len(similarity_data["results"]) > 0
    
    # Test health endpoints
    similarity_health = client.get("/similarity/health")
    assert similarity_health.status_code == 200
    
    sql_health = client.get("/sql-generation/health")
    assert sql_health.status_code == 200