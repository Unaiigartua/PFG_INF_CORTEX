import pytest
from unittest.mock import patch

def test_extract_entities_english(client, mock_medical_entities):
    """Test English medical entity extraction"""
    with patch('app.medical.ner.extract_medical_terms', return_value=mock_medical_entities):
        response = client.post("/extract", json={"text": "Patient has diabetes"})
        
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data
        assert len(data["entities"]) == 1
        assert data["entities"][0]["word"] == "diabetes"
        # El modelo real usa "Disease_disorder" en lugar de "CONDITION"
        assert data["entities"][0]["entity_group"] in ["CONDITION", "Disease_disorder"]

def test_extract_entities_spanish(client, mock_medical_entities):
    """Test Spanish medical entity extraction"""
    with patch('app.medical.ner_es.extract_medical_terms_es', return_value=mock_medical_entities):
        response = client.post("/extractEs", json={"text": "Paciente tiene diabetes"})
        
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data
        assert len(data["entities"]) == 1

def test_extract_entities_empty_text(client):
    """Test entity extraction with empty text"""
    with patch('app.medical.ner.extract_medical_terms', return_value=[]):
        response = client.post("/extract", json={"text": ""})
        
        assert response.status_code == 200
        data = response.json()
        assert data["entities"] == []

def test_extract_entities_real_service(client):
    """Test entity extraction with real service (no mocks)"""
    response = client.post("/extract", json={"text": "Patient has diabetes and hypertension"})
    
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    # Con el servicio real, puede detectar múltiples entidades
    assert isinstance(data["entities"], list)
