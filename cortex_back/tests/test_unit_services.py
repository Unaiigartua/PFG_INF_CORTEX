import pytest
from unittest.mock import patch, MagicMock
from app.sql_generation.service import SQLGenerationService
from app.sql_generation.models import SQLGenerationRequest, MedicalTerm

@pytest.fixture
def mock_dependencies():
    """Mock all external dependencies for SQLGenerationService"""
    with patch('app.sql_generation.service.OllamaClient') as mock_ollama, \
         patch('app.sql_generation.service.SQLValidator') as mock_validator, \
         patch('app.sql_generation.service.RAGRetriever') as mock_rag:
        
        # Configure mocks
        mock_ollama_instance = MagicMock()
        mock_ollama_instance.is_ollama_running.return_value = True
        mock_ollama_instance.check_model_availability.return_value = True
        mock_ollama.return_value = mock_ollama_instance
        
        mock_validator_instance = MagicMock()
        mock_validator.return_value = mock_validator_instance
        
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance
        
        yield {
            'ollama': mock_ollama_instance,
            'validator': mock_validator_instance,
            'rag': mock_rag_instance
        }

def test_sql_service_init(mock_dependencies):
    """Test SQLGenerationService initialization"""
    service = SQLGenerationService()
    
    assert service.model_name == "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
    assert service.max_attempts == 3
    assert service.timeout == 180

def test_sql_service_generate_sql_success(mock_dependencies):
    """Test successful SQL generation"""
    # Setup mocks
    mock_dependencies['ollama'].generate.return_value = "SELECT COUNT(*) FROM person;"
    mock_dependencies['validator'].clean_generated_sql.return_value = "SELECT COUNT(*) FROM person;"
    mock_dependencies['validator'].validate_sql_syntax.return_value = None
    mock_dependencies['validator'].test_sql_execution.return_value = {
        'executable': True,
        'error': None,
        'error_type': None
    }
    mock_dependencies['rag'].get_similar_examples.return_value = []
    
    service = SQLGenerationService()
    request = SQLGenerationRequest(
        question="How many patients are there?",
        medical_terms=[MedicalTerm(term="patient", concept_id="116154003")]
    )
    
    result = service.generate_sql(request)
    
    assert result.question == "How many patients are there?"
    assert result.generated_sql == "SELECT COUNT(*) FROM person;"
    assert result.is_executable is True
    assert result.attempts_count == 1
    assert result.error_message is None

def test_sql_service_generate_sql_ollama_down(mock_dependencies):
    """Test SQL generation when Ollama is down"""
    mock_dependencies['ollama'].is_ollama_running.return_value = False
    
    service = SQLGenerationService()
    request = SQLGenerationRequest(question="test", medical_terms=[])
    
    result = service.generate_sql(request)
    
    assert result.is_executable is False
    assert "Ollama no está ejecutándose" in result.error_message
    assert result.attempts_count == 0

def test_sql_service_generate_sql_model_unavailable(mock_dependencies):
    """Test SQL generation when model is unavailable"""
    mock_dependencies['ollama'].is_ollama_running.return_value = True
    mock_dependencies['ollama'].check_model_availability.return_value = False
    
    service = SQLGenerationService()
    request = SQLGenerationRequest(question="test", medical_terms=[])
    
    result = service.generate_sql(request)
    
    assert result.is_executable is False
    assert "no está disponible" in result.error_message

def test_sql_service_generate_sql_syntax_error_retry(mock_dependencies):
    """Test SQL generation with syntax error and retry"""
    # First attempt fails, second succeeds
    mock_dependencies['ollama'].generate.side_effect = [
        "SELCT COUNT(*) FROM person;",  # Syntax error
        "SELECT COUNT(*) FROM person;"   # Valid SQL
    ]
    mock_dependencies['validator'].clean_generated_sql.side_effect = [
        "SELCT COUNT(*) FROM person;",
        "SELECT COUNT(*) FROM person;"
    ]
    mock_dependencies['validator'].validate_sql_syntax.side_effect = [
        "Syntax error: near SELCT",  # First attempt error
        None  # Second attempt success
    ]
    mock_dependencies['validator'].test_sql_execution.return_value = {
        'executable': True,
        'error': None,
        'error_type': None
    }
    mock_dependencies['rag'].get_similar_examples.return_value = []
    
    service = SQLGenerationService()
    request = SQLGenerationRequest(question="test", medical_terms=[])
    
    result = service.generate_sql(request)
    
    assert result.is_executable is True
    assert result.attempts_count == 2
    assert mock_dependencies['ollama'].generate.call_count == 2

def test_sql_service_generate_sql_max_attempts(mock_dependencies):
    """Test SQL generation reaching max attempts"""
    mock_dependencies['ollama'].generate.return_value = "INVALID SQL"
    mock_dependencies['validator'].clean_generated_sql.return_value = "INVALID SQL"
    mock_dependencies['validator'].validate_sql_syntax.return_value = "Syntax error"
    mock_dependencies['rag'].get_similar_examples.return_value = []
    
    service = SQLGenerationService()
    request = SQLGenerationRequest(question="test", medical_terms=[])
    
    result = service.generate_sql(request)
    
    assert result.is_executable is False
    assert result.attempts_count == 3
    assert "Syntax error" in result.error_message

def test_sql_service_generate_sql_with_similar_example(mock_dependencies):
    """Test SQL generation using similar example"""
    similar_example = {
        "question": "How many patients have diabetes?",
        "sql": "SELECT COUNT(*) FROM person WHERE condition_concept_id = 201826;",
        "score": 0.85,
        "row_id": 1
    }
    
    mock_dependencies['rag'].get_similar_examples.return_value = [similar_example]
    mock_dependencies['ollama'].generate.return_value = "SELECT COUNT(*) FROM person;"
    mock_dependencies['validator'].clean_generated_sql.return_value = "SELECT COUNT(*) FROM person;"
    mock_dependencies['validator'].validate_sql_syntax.return_value = None
    mock_dependencies['validator'].test_sql_execution.return_value = {
        'executable': True,
        'error': None,
        'error_type': None
    }
    
    service = SQLGenerationService()
    request = SQLGenerationRequest(question="Count patients", medical_terms=[])
    
    result = service.generate_sql(request)
    
    assert result.similar_example is not None
    assert result.similar_example.score == 0.85
    assert "diabetes" in result.similar_example.question

def test_sql_service_create_prompt_initial(mock_dependencies):
    """Test initial prompt creation"""
    service = SQLGenerationService()
    
    medical_terms = [
        MedicalTerm(term="diabetes", concept_id="201826"),
        MedicalTerm(term="hypertension", concept_id="320128")
    ]
    
    similar_example = {
        "question": "Find diabetic patients",
        "sql": "SELECT * FROM person WHERE condition_concept_id = 201826;"
    }
    
    prompt = service._create_prompt(
        question="How many patients have diabetes and hypertension?",
        medical_terms=medical_terms,
        similar_example=similar_example,
        iteration=1
    )
    
    assert "How many patients have diabetes and hypertension?" in prompt
    assert "diabetes → 201826" in prompt
    assert "hypertension → 320128" in prompt
    assert "Find diabetic patients" in prompt
    assert "Generate ONLY SQL code" in prompt

def test_sql_service_create_prompt_correction(mock_dependencies):
    """Test correction prompt creation"""
    service = SQLGenerationService()
    
    medical_terms = [MedicalTerm(term="diabetes", concept_id="201826")]
    
    prompt = service._create_prompt(
        question="How many patients have diabetes?",
        medical_terms=medical_terms,
        similar_example=None,
        iteration=2,
        previous_sql="SELCT COUNT(*) FROM person;",
        error_msg="Syntax error near SELCT"
    )
    
    assert "Fix this SQL error" in prompt
    assert "SELCT COUNT(*)" in prompt
    assert "Syntax error near SELCT" in prompt
    assert "Fixed SQL:" in prompt

def test_sql_service_format_medical_terms(mock_dependencies):
    """Test medical terms formatting"""
    service = SQLGenerationService()
    
    # Test with medical terms
    medical_terms = [
        MedicalTerm(term="diabetes", concept_id="201826"),
        MedicalTerm(term="hypertension", concept_id="320128")
    ]
    
    formatted = service._format_medical_terms(medical_terms)
    assert "- diabetes → 201826" in formatted
    assert "- hypertension → 320128" in formatted
    
    # Test with empty list
    formatted_empty = service._format_medical_terms([])
    assert "No specific medical codes provided" in formatted_empty
