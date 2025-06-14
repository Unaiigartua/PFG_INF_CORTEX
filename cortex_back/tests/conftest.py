import pytest
import tempfile
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

# Añadir el directorio padre al path para importar app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.auth.database import Base as AuthBase, get_auth_db
from app.auth.models import User, QueryLog

# Test database setup
@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_url = f"sqlite:///{tmp_file.name}"
        engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
        AuthBase.metadata.create_all(bind=engine)
        yield engine
        os.unlink(tmp_file.name)

@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session with rollback"""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(test_db_session):
    """FastAPI test client with test database"""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_auth_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_db_session):
    """Create test user"""
    from app.auth.security import hash_password
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        is_active=True
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    login_data = {
        "username": test_user.email,
        "password": "testpassword123"
    }
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_medical_entities():
    """Mock medical entity extraction"""
    return [
        {
            "word": "diabetes",
            "entity_group": "CONDITION",
            "score": 0.95,
            "start": 0,
            "end": 8
        }
    ]

@pytest.fixture
def mock_similar_terms():
    """Mock similar terms response"""
    return [
        {
            "term": "diabetes mellitus",
            "preferred_term": "Diabetes mellitus",
            "concept_id": "201826",
            "similarity": 0.95,
            "semantic_tag": "disorder"
        }
    ]

@pytest.fixture
def sample_query_log(test_db_session, test_user):
    """Create sample query log entry"""
    query_log = QueryLog(
        user_id=test_user.id,
        title="Test diabetes query",
        question="How many patients have diabetes?",
        medical_terms=["diabetes"],
        generated_sql="SELECT COUNT(*) FROM person p JOIN condition_occurrence co ON p.person_id = co.person_id WHERE co.condition_concept_id = 201826;",
        is_executable=True,
        attempts_count=1,
        processing_time=2.5
    )
    test_db_session.add(query_log)
    test_db_session.commit()
    test_db_session.refresh(query_log)
    return query_log