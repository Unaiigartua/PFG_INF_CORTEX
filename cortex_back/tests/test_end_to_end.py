import pytest
import time
from unittest.mock import patch

def test_complete_workflow_mock_services(client):
    """Test complete workflow with all services mocked"""
    
    # 1. Register user
    user_data = {"email": "e2e@test.com", "password": "testpass123"}
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200
    
    # 2. Login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test medical entity extraction (English)
    mock_entities_en = [
        {"word": "diabetes", "entity_group": "CONDITION", "score": 0.95, "start": 0, "end": 8},
        {"word": "hypertension", "entity_group": "CONDITION", "score": 0.90, "start": 13, "end": 25}
    ]
    
    with patch('app.medical.ner.extract_medical_terms', return_value=mock_entities_en):
        extract_response = client.post("/extract", json={"text": "diabetes and hypertension"})
        assert extract_response.status_code == 200
        entities = extract_response.json()["entities"]
        assert len(entities) == 2
        assert entities[0]["word"] == "diabetes"
        assert entities[1]["word"] == "hypertension"
    
    # 4. Test medical entity extraction (Spanish)
    mock_entities_es = [{"word": "diabetes", "entity_group": "CONDITION", "score": 0.95, "start": 0, "end": 8}]
    
    with patch('app.medical.ner_es.extract_medical_terms_es', return_value=mock_entities_es):
        extract_es_response = client.post("/extractEs", json={"text": "diabetes mellitus"})
        assert extract_es_response.status_code == 200
        entities_es = extract_es_response.json()["entities"]
        assert len(entities_es) == 1
    
    # 5. Test similarity search for each entity
    mock_similar_diabetes = [
        {
            "term": "diabetes mellitus",
            "preferred_term": "Diabetes mellitus",
            "concept_id": "201826",
            "similarity": 0.95,
            "semantic_tag": "disorder"
        }
    ]
    
    mock_similar_hypertension = [
        {
            "term": "hypertensive disorder",
            "preferred_term": "Hypertensive disorder",
            "concept_id": "320128",
            "similarity": 0.92,
            "semantic_tag": "disorder"
        }
    ]
    
    with patch('app.medical.similarity_bd.get_similar_terms_bd', return_value=mock_similar_diabetes):
        diabetes_response = client.post("/similar_db", json={"term": "diabetes"})
        assert diabetes_response.status_code == 200
        diabetes_terms = diabetes_response.json()["results"]
        assert len(diabetes_terms) == 1
        assert diabetes_terms[0]["concept_id"] == "201826"
    
    with patch('app.medical.similarity_bd.get_similar_terms_bd', return_value=mock_similar_hypertension):
        hypertension_response = client.post("/similar_db", json={"term": "hypertension"})
        assert hypertension_response.status_code == 200
        hypertension_terms = hypertension_response.json()["results"]
        assert len(hypertension_terms) == 1
        assert hypertension_terms[0]["concept_id"] == "320128"
    
    # 6. Test SQL generation with validated terms
    mock_sql_response = {
        "question": "How many patients have diabetes and hypertension?",
        "generated_sql": """SELECT COUNT(DISTINCT p.person_id) 
                           FROM person p 
                           JOIN condition_occurrence co1 ON p.person_id = co1.person_id 
                           JOIN condition_occurrence co2 ON p.person_id = co2.person_id 
                           WHERE co1.condition_concept_id = 201826 
                           AND co2.condition_concept_id = 320128;""",
        "is_executable": True,
        "attempts_count": 1,
        "error_message": None,
        "similar_example": {
            "question": "Find patients with multiple conditions",
            "sql": "SELECT COUNT(*) FROM person WHERE...",
            "score": 0.78
        }
    }
    
    sql_request = {
        "question": "How many patients have diabetes and hypertension?",
        "medical_terms": [
            {"term": "diabetes", "concept_id": "201826"},
            {"term": "hypertension", "concept_id": "320128"}
        ]
    }
    
    with patch('app.sql_generation.service.SQLGenerationService.generate_sql', 
               return_value=type('MockResponse', (), mock_sql_response)()):
        sql_response = client.post("/sql-generation/", json=sql_request, headers=headers)
        assert sql_response.status_code == 200
        sql_data = sql_response.json()
        assert sql_data["is_executable"] is True
        assert "SELECT COUNT(DISTINCT p.person_id)" in sql_data["generated_sql"]
        assert sql_data["similar_example"] is not None
    
    # 7. Test query history
    history_response = client.get("/queries/history", headers=headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["question"] == sql_request["question"]
    assert history[0]["is_executable"] is True
    
    # 8. Test getting specific query details
    query_id = history[0]["id"]
    detail_response = client.get(f"/queries/{query_id}", headers=headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["generated_sql"] is not None
    assert detail["medical_terms"] == ["diabetes", "hypertension"]
    
    # 9. Test deleting query
    delete_response = client.delete(f"/queries/{query_id}", headers=headers)
    assert delete_response.status_code == 200
    
    # Verify deletion
    deleted_history = client.get("/queries/history", headers=headers)
    assert len(deleted_history.json()) == 0

def test_error_scenarios_workflow(client, auth_headers):
    """Test various error scenarios in the workflow"""
    
    # 1. Test entity extraction with empty text
    with patch('app.medical.ner.extract_medical_terms', return_value=[]):
        empty_response = client.post("/extract", json={"text": ""})
        assert empty_response.status_code == 200
        assert empty_response.json()["entities"] == []
    
    # 2. Test similarity search with unknown term
    with patch('app.medical.similarity_bd.get_similar_terms_bd', return_value=[]):
        unknown_response = client.post("/similar_db", json={"term": "unknownmedicalterm"})
        assert unknown_response.status_code == 200
        assert unknown_response.json()["results"] == []
    
    # 3. Test SQL generation failure
    mock_failed_sql = {
        "question": "Invalid medical query",
        "generated_sql": "",
        "is_executable": False,
        "attempts_count": 3,
        "error_message": "Could not generate valid SQL after 3 attempts",
        "similar_example": None
    }
    
    failed_request = {
        "question": "Invalid medical query",
        "medical_terms": []
    }
    
    with patch('app.sql_generation.service.SQLGenerationService.generate_sql',
               return_value=type('MockResponse', (), mock_failed_sql)()):
        failed_response = client.post("/sql-generation/", json=failed_request, headers=auth_headers)
        assert failed_response.status_code == 200
        failed_data = failed_response.json()
        assert failed_data["is_executable"] is False
        assert failed_data["attempts_count"] == 3
        assert "Could not generate valid SQL" in failed_data["error_message"]
    
    # 4. Test accessing non-existent query
    nonexistent_response = client.get("/queries/999999", headers=auth_headers)
    assert nonexistent_response.status_code == 404

def test_performance_workflow(client, auth_headers):
    """Test performance aspects of the workflow"""
    
    # Test multiple rapid requests
    start_time = time.time()
    
    mock_entities = [{"word": "test", "entity_group": "CONDITION", "score": 0.9, "start": 0, "end": 4}]
    
    with patch('app.medical.ner.extract_medical_terms', return_value=mock_entities):
        responses = []
        for i in range(5):
            response = client.post("/extract", json={"text": f"test condition {i}"})
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Should complete 5 requests in reasonable time (less than 5 seconds with mocks)
    assert total_time < 5.0

def test_concurrent_users_simulation(client):
    """Simulate multiple users using the system concurrently"""
    
    users = []
    tokens = []
    
    # Create multiple test users
    for i in range(3):
        user_data = {"email": f"user{i}@test.com", "password": "testpass123"}
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        login_data = {"username": user_data["email"], "password": user_data["password"]}
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        users.append(user_data)
        tokens.append({"Authorization": f"Bearer {token}"})
    
    # Each user performs different medical queries
    queries = [
        {"question": "How many patients have diabetes?", "terms": [{"term": "diabetes", "concept_id": "201826"}]},
        {"question": "Find patients with heart disease", "terms": [{"term": "heart disease", "concept_id": "313217"}]},
        {"question": "Count female patients", "terms": [{"term": "female", "concept_id": "8532"}]}
    ]
    
    mock_sql_responses = [
        {
            "question": queries[i]["question"],
            "generated_sql": f"SELECT COUNT(*) FROM person WHERE condition_concept_id = {queries[i]['terms'][0]['concept_id']};",
            "is_executable": True,
            "attempts_count": 1,
            "error_message": None,
            "similar_example": None
        }
        for i in range(3)
    ]
    
    # Each user generates SQL
    with patch('app.sql_generation.service.SQLGenerationService.generate_sql') as mock_generate:
        mock_generate.side_effect = [
            type('MockResponse', (), response)() for response in mock_sql_responses
        ]
        
        for i, (token, query) in enumerate(zip(tokens, queries)):
            sql_request = {
                "question": query["question"],
                "medical_terms": query["terms"]
            }
            
            response = client.post("/sql-generation/", json=sql_request, headers=token)
            assert response.status_code == 200
            assert response.json()["is_executable"] is True
    
    # Each user should have their own query in history
    for i, token in enumerate(tokens):
        history_response = client.get("/queries/history", headers=token)
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) == 1
        assert history[0]["question"] == queries[i]["question"]

@pytest.mark.parametrize("invalid_input", [
    {"text": None},
    {"text": 123},
    {"text": ["invalid", "list"]},
    {}
])
def test_input_validation_edge_cases(client, invalid_input):
    """Test input validation with various invalid inputs"""
    
    # Test entity extraction with invalid inputs
    response = client.post("/extract", json=invalid_input)
    # Should either return 422 (validation error) or handle gracefully
    assert response.status_code in [200, 422]

@pytest.mark.parametrize("sql_scenario", [
    {
        "name": "simple_count",
        "question": "How many patients?",
        "expected_sql_pattern": "SELECT COUNT(*) FROM person"
    },
    {
        "name": "condition_filter",
        "question": "Patients with diabetes",
        "expected_sql_pattern": "condition_concept_id = 201826"
    },
    {
        "name": "gender_filter", 
        "question": "Female patients",
        "expected_sql_pattern": "gender_concept_id = 8532"
    }
])
def test_sql_generation_patterns(client, auth_headers, sql_scenario):
    """Test different SQL generation patterns"""
    
    mock_response = {
        "question": sql_scenario["question"],
        "generated_sql": f"SELECT COUNT(*) FROM person WHERE {sql_scenario['expected_sql_pattern']};",
        "is_executable": True,
        "attempts_count": 1,
        "error_message": None,
        "similar_example": None
    }
    
    request = {
        "question": sql_scenario["question"],
        "medical_terms": []
    }
    
    with patch('app.sql_generation.service.SQLGenerationService.generate_sql',
               return_value=type('MockResponse', (), mock_response)()):
        response = client.post("/sql-generation/", json=request, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert sql_scenario["expected_sql_pattern"] in data["generated_sql"]