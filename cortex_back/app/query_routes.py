from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.auth.models import QueryLog
from app.query_schemas import QueryLogCreate, QueryLogResponse, QueryLogSummary
from app.auth.database import get_auth_db
from app.auth.routes import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/queries", tags=["queries"])

def generate_title(question: str, max_length: int = 80) -> str:
    """Generar título a partir de la pregunta (primeros N caracteres)"""
    if len(question) <= max_length:
        return question
    return question[:max_length-3] + "..."

@router.post("/", response_model=QueryLogResponse)
def create_query(
    query_data: QueryLogCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    """Crear nueva consulta en el historial"""
    try:
        # Generar título automáticamente
        title = generate_title(query_data.question)
        
        # Crear nueva entrada
        query_log = QueryLog(
            user_id=current_user.id,
            title=title,
            question=query_data.question,
            medical_terms=query_data.medical_terms,
            generated_sql=query_data.generated_sql,
            is_executable=query_data.is_executable,
            attempts_count=query_data.attempts_count,
            error_message=query_data.error_message,
            processing_time=query_data.processing_time,
            results_count=query_data.results_count
        )
        
        db.add(query_log)
        db.commit()
        db.refresh(query_log)
        
        logger.info(f"Nueva consulta creada para usuario {current_user.id}: {query_log.id}")
        return query_log
        
    except Exception as e:
        logger.error(f"Error creando consulta: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno creando la consulta"
        )

@router.get("/history", response_model=List[QueryLogSummary])
def get_user_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_auth_db),
    limit: int = 50,
    offset: int = 0
):
    """Obtener historial de consultas del usuario autenticado"""
    try:
        queries = db.query(QueryLog)\
            .filter(QueryLog.user_id == current_user.id)\
            .order_by(QueryLog.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        logger.info(f"Historial obtenido para usuario {current_user.id}: {len(queries)} consultas")
        return queries
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo el historial"
        )

@router.get("/{query_id}", response_model=QueryLogResponse)
def get_query_by_id(
    query_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    """Obtener consulta específica por ID (solo si pertenece al usuario)"""
    try:
        query = db.query(QueryLog)\
            .filter(QueryLog.id == query_id, QueryLog.user_id == current_user.id)\
            .first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada o no tienes permisos para acceder"
            )
        
        logger.info(f"Consulta {query_id} obtenida por usuario {current_user.id}")
        return query
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo consulta {query_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo la consulta"
        )

@router.delete("/{query_id}")
def delete_query(
    query_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    """Eliminar consulta específica (solo si pertenece al usuario)"""
    try:
        query = db.query(QueryLog)\
            .filter(QueryLog.id == query_id, QueryLog.user_id == current_user.id)\
            .first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada o no tienes permisos para eliminar"
            )
        
        db.delete(query)
        db.commit()
        
        logger.info(f"Consulta {query_id} eliminada por usuario {current_user.id}")
        return {"message": "Consulta eliminada exitosamente", "id": query_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando consulta {query_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno eliminando la consulta"
        )