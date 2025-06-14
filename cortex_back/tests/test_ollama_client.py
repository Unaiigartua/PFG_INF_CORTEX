import pytest
import requests
from unittest.mock import patch, MagicMock
from app.sql_generation.ollama_client import OllamaClient

@pytest.fixture
def ollama_client():
    """Create Ollama client for testing"""
    return OllamaClient("http://localhost:11434")

def test_ollama_client_init(ollama_client):
    """Test Ollama client initialization"""
    assert ollama_client.base_url == "http://localhost:11434"
    assert ollama_client.session is not None

def test_is_ollama_running_success(ollama_client):
    """Test successful Ollama connection check"""
    with patch.object(ollama_client.session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = ollama_client.is_ollama_running()
        assert result is True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

def test_is_ollama_running_failure(ollama_client):
    """Test Ollama connection check when service is down"""
    with patch.object(ollama_client.session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = ollama_client.is_ollama_running()
        assert result is False

def test_list_models_success(ollama_client):
    """Test successful model listing"""
    mock_models_response = {
        "models": [
            {"name": "llama2:7b"},
            {"name": "deepseek-coder-v2:16b-lite-instruct-q4_K_M"}
        ]
    }
    
    with patch.object(ollama_client.session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_models_response
        mock_get.return_value = mock_response
        
        models = ollama_client.list_models()
        assert len(models) == 2
        assert "llama2:7b" in models
        assert "deepseek-coder-v2:16b-lite-instruct-q4_K_M" in models

def test_list_models_failure(ollama_client):
    """Test model listing when request fails"""
    with patch.object(ollama_client.session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException()
        
        models = ollama_client.list_models()
        assert models == []

def test_generate_success(ollama_client):
    """Test successful text generation"""
    mock_response_data = {
        "response": "SELECT COUNT(*) FROM person WHERE condition_concept_id = 201826;"
    }
    
    with patch.object(ollama_client.session, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response
        
        result = ollama_client.generate(
            model_name="test-model",
            prompt="Generate SQL for diabetes patients",
            temperature=0.1,
            max_tokens=200
        )
        
        assert result == mock_response_data["response"]
        
        # Verify the request payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["model"] == "test-model"
        assert payload["prompt"] == "Generate SQL for diabetes patients"
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0.1
        assert payload["options"]["num_predict"] == 200

def test_generate_failure(ollama_client):
    """Test text generation when request fails"""
    with patch.object(ollama_client.session, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        result = ollama_client.generate(
            model_name="test-model",
            prompt="test prompt"
        )
        
        assert result is None

def test_generate_timeout(ollama_client):
    """Test text generation with timeout"""
    with patch.object(ollama_client.session, 'post') as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout()
        
        result = ollama_client.generate(
            model_name="test-model",
            prompt="test prompt",
            timeout=60
        )
        
        assert result is None

def test_check_model_availability_exists(ollama_client):
    """Test checking for available model"""
    with patch.object(ollama_client, 'list_models') as mock_list:
        mock_list.return_value = [
            "llama2:7b",
            "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
        ]
        
        result = ollama_client.check_model_availability("deepseek-coder-v2:16b-lite-instruct-q4_K_M")
        assert result is True
        
        result = ollama_client.check_model_availability("deepseek-coder")
        assert result is True  # Partial match

def test_check_model_availability_not_exists(ollama_client):
    """Test checking for unavailable model"""
    with patch.object(ollama_client, 'list_models') as mock_list:
        mock_list.return_value = ["llama2:7b"]
        
        result = ollama_client.check_model_availability("nonexistent-model")
        assert result is False

def test_generate_with_default_options(ollama_client):
    """Test generation with default options"""
    mock_response_data = {"response": "test response"}
    
    with patch.object(ollama_client.session, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response
        
        result = ollama_client.generate(
            model_name="test-model",
            prompt="test prompt"
        )
        
        assert result == "test response"
        
        # Check default values were used
        payload = mock_post.call_args[1]["json"]
        assert payload["options"]["temperature"] == 0.05  # Default
        assert payload["options"]["top_p"] == 0.9  # Default
        assert payload["options"]["num_predict"] == 400  # Default
