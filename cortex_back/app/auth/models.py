from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, func, Float, JSON
from sqlalchemy.orm import relationship
from app.auth.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    queries = relationship("QueryLog", back_populates="user")

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    # IDs y relaciones
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la consulta original
    title = Column(String(200), nullable=True)  # Resumen/título generado
    question = Column(Text, nullable=False)     # Pregunta en lenguaje natural
    medical_terms = Column(JSON, nullable=True)  # Términos médicos validados
    
    # Información del resultado
    generated_sql = Column(Text, nullable=True)     # SQL generado
    is_executable = Column(Boolean, nullable=False) # Si el SQL es ejecutable
    attempts_count = Column(Integer, default=1)     # Número de intentos
    error_message = Column(Text, nullable=True)     # Error final si falló
    
    # Información de rendimiento
    processing_time = Column(Float, nullable=True)  # Tiempo total en segundos
    
    # Metadatos
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación
    user = relationship("User", back_populates="queries")