from pydantic import BaseModel
from typing import List, Optional

class MedicalTerm(BaseModel):
    term: str
    concept_id: str

class SQLGenerationRequest(BaseModel):
    question: str
    medical_terms: List[MedicalTerm]

class SimilarExample(BaseModel):
    question: str
    sql: str
    score: float

class SQLGenerationResponse(BaseModel):
    question: str
    generated_sql: str
    is_executable: bool
    error_message: Optional[str] = None
    attempts_count: int
    similar_example: Optional[SimilarExample] = None


class SQLValidationRequest(BaseModel):
    sql_query: str
    question: Optional[str] = None

class SQLValidationResponse(BaseModel):
    sql_query: str
    is_valid: bool
    is_executable: bool
    syntax_error: Optional[str] = None
    execution_error: Optional[str] = None
    execution_time: Optional[float] = None
    row_count: Optional[int] = None
    question: Optional[str] = None