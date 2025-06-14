import pytest
import tempfile
import os
from pathlib import Path
from app.sql_generation.sql_validator import SQLValidator

@pytest.fixture
def test_omop_db():
    """Create a temporary test OMOP database"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name
        
        # Create basic OMOP tables for testing
        import sqlite3
        conn = sqlite3.connect(db_path)
        
        # Create basic OMOP tables
        conn.execute("""
            CREATE TABLE person (
                person_id INTEGER PRIMARY KEY,
                gender_concept_id INTEGER,
                year_of_birth INTEGER,
                race_concept_id INTEGER
            )
        """)
        
        conn.execute("""
            CREATE TABLE condition_occurrence (
                condition_occurrence_id INTEGER PRIMARY KEY,
                person_id INTEGER,
                condition_concept_id INTEGER,
                condition_start_date DATE,
                FOREIGN KEY (person_id) REFERENCES person(person_id)
            )
        """)
        
        # Insert test data
        conn.execute("INSERT INTO person VALUES (1, 8532, 1980, 8527)")
        conn.execute("INSERT INTO person VALUES (2, 8507, 1975, 8527)")
        conn.execute("INSERT INTO condition_occurrence VALUES (1, 1, 201826, '2023-01-01')")
        
        conn.commit()
        conn.close()
        
        yield db_path
        os.unlink(db_path)

@pytest.fixture
def sql_validator(test_omop_db):
    """Create SQL validator with test database"""
    return SQLValidator(test_omop_db)

def test_validate_sql_syntax_valid(sql_validator):
    """Test validation of valid SQL"""
    valid_sql = "SELECT COUNT(*) FROM person WHERE gender_concept_id = 8532;"
    error = sql_validator.validate_sql_syntax(valid_sql)
    assert error is None

def test_validate_sql_syntax_missing_select(sql_validator):
    """Test validation fails for SQL without SELECT"""
    invalid_sql = "FROM person WHERE gender_concept_id = 8532;"
    error = sql_validator.validate_sql_syntax(invalid_sql)
    assert "SELECT y FROM" in error

def test_validate_sql_syntax_prohibited_operations(sql_validator):
    """Test validation fails for prohibited operations"""
    prohibited_sqls = [
        "SELECT FROM DELETE FROM person;",
        "SELECT FROM INSERT INTO person VALUES (3, 8532, 1990, 8527);",
        "SELECT FROM UPDATE person SET year_of_birth = 1990;",
        "SELECT FROM DROP TABLE person;",
        "SELECT FROM CREATE TABLE test (id INTEGER);",
        "SELECT FROM TRUNCATE TABLE person;",
        "SELECT FROM ALTER TABLE person ADD COLUMN test INTEGER;"
    ]
    
    for sql in prohibited_sqls:
        error = sql_validator.validate_sql_syntax(sql)
        assert error is not None
        assert "Operación prohibida" in error

def test_validate_sql_syntax_empty(sql_validator):
    """Test validation fails for empty SQL"""
    error = sql_validator.validate_sql_syntax("")
    assert "SQL vacío" in error
    
    error = sql_validator.validate_sql_syntax(";")
    assert "SQL vacío" in error

def test_validate_sql_syntax_too_long(sql_validator):
    """Test validation fails for very long SQL"""
    long_sql = "SELECT " + ", ".join([f"column_{i}" for i in range(1000)]) + " FROM person;"
    error = sql_validator.validate_sql_syntax(long_sql)
    assert "SQL demasiado largo" in error

def test_validate_sql_syntax_too_many_selects(sql_validator):
    """Test validation fails for too many nested SELECTs"""
    nested_sql = "SELECT * FROM (" * 25 + "SELECT * FROM person" + ")" * 25 + ";"
    error = sql_validator.validate_sql_syntax(nested_sql)
    assert "Demasiados SELECT anidados" in error

def test_clean_generated_sql_code_blocks(sql_validator):
    """Test cleaning SQL from code blocks"""
    text_with_sql = """
    Here's the SQL query:
    ```sql
    SELECT COUNT(*) FROM person 
    WHERE gender_concept_id = 8532;
    ```
    This query counts female patients.
    """
    
    cleaned = sql_validator.clean_generated_sql(text_with_sql)
    assert "SELECT COUNT(*)" in cleaned
    assert "Here's the SQL" not in cleaned
    assert cleaned.endswith(";")

def test_clean_generated_sql_multiple_formats(sql_validator):
    """Test cleaning SQL from various formats"""
    formats = [
        "```sql\nSELECT * FROM person;\n```",
        "```\nSELECT * FROM person;\n```",
        "SQL:\nSELECT * FROM person;",
        "SELECT * FROM person;"
    ]
    
    for text in formats:
        cleaned = sql_validator.clean_generated_sql(text)
        assert "SELECT * FROM person" in cleaned
        assert cleaned.endswith(";")

def test_clean_generated_sql_with_comments(sql_validator):
    """Test cleaning SQL with comments"""
    text_with_comments = """
    -- This is a comment about the query
    SELECT COUNT(*) FROM person 
    -- Filter by gender
    WHERE gender_concept_id = 8532;
    -- End of query
    """
    
    cleaned = sql_validator.clean_generated_sql(text_with_comments)
    assert "SELECT COUNT(*)" in cleaned
    assert "This is a comment" not in cleaned

def test_test_sql_execution_valid(sql_validator):
    """Test execution of valid SQL"""
    valid_sql = "SELECT COUNT(*) FROM person;"
    result = sql_validator.test_sql_execution(valid_sql)
    
    assert result["executable"] is True
    assert result["error"] is None
    assert result["row_count"] == 1
    assert result["execution_time"] is not None

def test_test_sql_execution_with_results(sql_validator):
    """Test execution returning multiple rows"""
    valid_sql = "SELECT person_id, gender_concept_id FROM person;"
    result = sql_validator.test_sql_execution(valid_sql)
    
    assert result["executable"] is True
    assert result["row_count"] == 2  # We inserted 2 test persons

def test_test_sql_execution_syntax_error(sql_validator):
    """Test execution with syntax error"""
    invalid_sql = "SELCT COUNT(*) FROM person;"  # Typo in SELECT
    result = sql_validator.test_sql_execution(invalid_sql)
    
    assert result["executable"] is False
    assert result["error"] is not None
    assert result["error_type"] in ["OperationalError", "DatabaseError"]

def test_test_sql_execution_table_not_found(sql_validator):
    """Test execution with non-existent table"""
    invalid_sql = "SELECT COUNT(*) FROM nonexistent_table;"
    result = sql_validator.test_sql_execution(invalid_sql)
    
    assert result["executable"] is False
    assert result["error"] is not None

def test_test_sql_execution_no_database(tmp_path):
    """Test execution when database doesn't exist"""
    nonexistent_db = tmp_path / "nonexistent.db"
    validator = SQLValidator(str(nonexistent_db))
    
    result = validator.test_sql_execution("SELECT 1;")
    
    assert result["executable"] is False
    assert "Base de datos OMOP no encontrada" in result["error"]
    assert result["error_type"] == "DatabaseNotFound"

@pytest.mark.parametrize("sql,expected_clean", [
    ("SELECT * FROM person", "SELECT * FROM person;"),
    ("SELECT * FROM person;", "SELECT * FROM person;"),
    ("  SELECT * FROM person  ", "SELECT * FROM person;"),
    ("SELECT *\nFROM person", "SELECT *\nFROM person;")
])
def test_clean_sql_text_semicolon(sql_validator, sql, expected_clean):
    """Test that cleaned SQL always ends with semicolon"""
    cleaned = sql_validator._clean_sql_text(sql)
    assert cleaned == expected_clean