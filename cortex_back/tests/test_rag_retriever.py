import pytest
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.sql_generation.rag_retriever import RAGRetriever, MedicalSQLRetriever

@pytest.fixture
def sample_dataset():
    """Create sample dataset for testing"""
    data = {
        "ID": [1, 2, 3],
        "QUESTION_EN": [
            "How many patients have diabetes?",
            "Find patients with heart disease",
            "Count female patients"
        ],
        "QUESTION_ES": [
            "¿Cuántos pacientes tienen diabetes?",
            "Encontrar pacientes con enfermedad cardíaca", 
            "Contar pacientes femeninas"
        ],
        "SQL_QUERY_RUNNABLE": [
            "SELECT COUNT(*) FROM person p JOIN condition_occurrence co ON p.person_id = co.person_id WHERE co.condition_concept_id = 201826;",
            "SELECT * FROM person p JOIN condition_occurrence co ON p.person_id = co.person_id WHERE co.condition_concept_id = 313217;",
            "SELECT COUNT(*) FROM person WHERE gender_concept_id = 8532;"
        ]
    }
    return pd.DataFrame(data)

@pytest.fixture
def test_dataset_file(sample_dataset):
    """Create temporary Excel file with test data"""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        sample_dataset.to_excel(tmp_file.name, index=False)
        yield Path(tmp_file.name)
        Path(tmp_file.name).unlink()

@pytest.fixture
def mock_sentence_transformer():
    """Mock sentence transformer model"""
    mock_model = MagicMock()
    mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    return mock_model

def test_medical_sql_retriever_init():
    """Test MedicalSQLRetriever initialization"""
    with patch('app.sql_generation.rag_retriever.SentenceTransformer') as mock_st:
        retriever = MedicalSQLRetriever()
        assert retriever.model is not None
        assert retriever.index is None
        assert retriever.metadata is None

def test_medical_sql_retriever_build(test_dataset_file, mock_sentence_transformer):
    """Test building RAG index from dataset"""
    with patch('app.sql_generation.rag_retriever.SentenceTransformer', return_value=mock_sentence_transformer):
        with patch('faiss.IndexFlatIP') as mock_index:
            with patch('faiss.normalize_L2'):
                with patch('faiss.write_index'):
                    mock_faiss_index = MagicMock()
                    mock_index.return_value = mock_faiss_index
                    
                    retriever = MedicalSQLRetriever()
                    retriever.build(test_dataset_file)
                    
                    assert retriever.index is not None
                    assert retriever.metadata is not None
                    assert len(retriever.metadata) == 6  # 3 questions × 2 languages

def test_medical_sql_retriever_load():
    """Test loading pre-built RAG index"""
    with patch('app.sql_generation.rag_retriever.SentenceTransformer'):
        with patch('faiss.read_index') as mock_read:
            with patch('pickle.load') as mock_pickle:
                with patch('pathlib.Path.exists', return_value=True):
                    mock_index = MagicMock()
                    mock_index.ntotal = 100
                    mock_read.return_value = mock_index
                    mock_pickle.return_value = [{"test": "metadata"}]
                    
                    retriever = MedicalSQLRetriever()
                    retriever.load()
                    
                    assert retriever.index is not None
                    assert retriever.metadata is not None

def test_medical_sql_retriever_load_file_not_found():
    """Test loading when index file doesn't exist"""
    with patch('app.sql_generation.rag_retriever.SentenceTransformer'):
        with patch('pathlib.Path.exists', return_value=False):
            retriever = MedicalSQLRetriever()
            
            with pytest.raises(FileNotFoundError):
                retriever.load()

def test_medical_sql_retriever_query(mock_sentence_transformer):
    """Test querying the RAG index"""
    with patch('app.sql_generation.rag_retriever.SentenceTransformer', return_value=mock_sentence_transformer):
        retriever = MedicalSQLRetriever()
        
        # Mock the index and metadata
        mock_index = MagicMock()
        mock_index.search.return_value = (
            [[0.9, 0.7]], [[0, 1]]  # scores, indices
        )
        retriever.index = mock_index
        retriever.metadata = [
            {"canonical_question": "How many patients have diabetes?", "sql": "SELECT COUNT(*) FROM person;"},
            {"canonical_question": "Find heart disease patients", "sql": "SELECT * FROM person;"}
        ]
        
        results = retriever.query("diabetes patients", k=2)
        
        assert len(results) == 2
        assert results[0][0] == 0.9  # score
        assert results[0][1]["canonical_question"] == "How many patients have diabetes?"

def test_rag_retriever_init():
    """Test RAGRetriever initialization"""
    retriever = RAGRetriever("test_dataset.xlsx")
    assert retriever.dataset_path == Path("test_dataset.xlsx")
    assert retriever._index_built is False

def test_rag_retriever_get_similar_examples_build_index(test_dataset_file):
    """Test getting similar examples when index needs to be built"""
    with patch('app.sql_generation.rag_retriever.MedicalSQLRetriever') as mock_retriever_class:
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = [
            (0.85, {
                "canonical_question": "How many patients have diabetes?",
                "sql": "SELECT COUNT(*) FROM person;",
                "row_id": 1
            })
        ]
        mock_retriever_class.return_value = mock_retriever
        
        rag_retriever = RAGRetriever(str(test_dataset_file))
        results = rag_retriever.get_similar_examples("diabetes", k=1)
        
        assert len(results) == 1
        assert results[0]["question"] == "How many patients have diabetes?"
        assert results[0]["score"] == 0.85
        assert "sql" in results[0]

def test_rag_retriever_get_similar_examples_already_built():
    """Test getting similar examples when index is already built"""
    with patch('app.sql_generation.rag_retriever.MedicalSQLRetriever') as mock_retriever_class:
        mock_retriever = MagicMock()
        mock_retriever_class.return_value = mock_retriever
        
        rag_retriever = RAGRetriever("test.xlsx")
        rag_retriever._index_built = True
        rag_retriever.retriever = mock_retriever
        
        mock_retriever.query.return_value = [
            (0.9, {"canonical_question": "test", "sql": "SELECT 1;", "row_id": 1})
        ]
        
        results = rag_retriever.get_similar_examples("test query")
        
        assert len(results) == 1
        mock_retriever.query.assert_called_once_with("test query", k=1)

def test_rag_retriever_get_similar_examples_error():
    """Test error handling in get_similar_examples"""
    with patch('app.sql_generation.rag_retriever.MedicalSQLRetriever') as mock_retriever_class:
        mock_retriever_class.side_effect = Exception("Database error")
        
        rag_retriever = RAGRetriever("nonexistent.xlsx")
        
        with pytest.raises(Exception):
            rag_retriever.get_similar_examples("test query")

def test_rag_retriever_no_dataset_file():
    """Test behavior when dataset file doesn't exist"""
    nonexistent_file = "nonexistent_dataset.xlsx"
    rag_retriever = RAGRetriever(nonexistent_file)
    
    with pytest.raises(FileNotFoundError):
        rag_retriever.get_similar_examples("test query")

def test_rag_retriever_format_similar_example():
    """Test formatting similar example for prompt"""
    rag_retriever = RAGRetriever("test.xlsx")
    
    example = {
        "question": "How many patients have diabetes?",
        "sql": "SELECT COUNT(*) FROM person WHERE condition_concept_id = 201826;",
        "score": 0.85
    }
    
    formatted = rag_retriever.format_similar_example(example)
    
    assert "Question: How many patients have diabetes?" in formatted
    assert "SQL: SELECT COUNT(*)" in formatted

def test_rag_retriever_format_empty_example():
    """Test formatting empty example"""
    rag_retriever = RAGRetriever("test.xlsx")
    
    formatted = rag_retriever.format_similar_example({})
    assert formatted == "No similar examples found."
    
    formatted = rag_retriever.format_similar_example(None)
    assert formatted == "No similar examples found."