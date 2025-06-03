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