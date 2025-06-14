from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Nuevos schemas para el sistema mejorado de QueryLog
class QueryLogCreate(BaseModel):
    question: str
    medical_terms: Optional[List[str]] = None
    generated_sql: Optional[str] = None
    is_executable: bool = False
    attempts_count: int = 1
    error_message: Optional[str] = None
    processing_time: Optional[float] = None

class QueryLogResponse(BaseModel):
    id: int
    title: Optional[str]
    question: str
    medical_terms: Optional[List[str]]
    generated_sql: Optional[str]
    is_executable: bool
    attempts_count: int
    error_message: Optional[str]
    processing_time: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True

class QueryLogSummary(BaseModel):
    """Schema para el historial (versión resumida)"""
    id: int
    title: Optional[str]
    question: str
    is_executable: bool
    attempts_count: int
    timestamp: datetime

    class Config:
        from_attributes = True