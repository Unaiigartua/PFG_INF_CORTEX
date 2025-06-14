from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import time

from .models import SQLGenerationRequest, SQLGenerationResponse
from .service import SQLGenerationService
from app.auth.routes import get_current_user
from app.auth.database import get_auth_db
from app.auth.models import QueryLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sql-generation", tags=["sql-generation"])

# Instancia global del servicio (se inicializa una vez)
sql_service = None

def get_sql_service() -> SQLGenerationService:
    """Dependencia para obtener el servicio de generación SQL"""
    global sql_service
    if sql_service is None:
        try:
            sql_service = SQLGenerationService()
            logger.info("Servicio de generación SQL inicializado")
        except Exception as e:
            logger.error(f"Error inicializando servicio SQL: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error inicializando el servicio de generación SQL"
            )
    return sql_service

def generate_title(question: str, max_length: int = 80) -> str:
    """Generar título a partir de la pregunta (primeros N caracteres)"""
    if len(question) <= max_length:
        return question
    return question[:max_length-3] + "..."

@router.post("/", response_model=SQLGenerationResponse)
def generate_sql(
    request: SQLGenerationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_auth_db),
    service: SQLGenerationService = Depends(get_sql_service)
):
    """
    Generar consulta SQL desde lenguaje natural.
    
    Requiere autenticación JWT y registra la consulta completa en los logs del usuario.
    """
    start_time = time.time()
    
    try:
        # Generar SQL
        logger.info(f"Generando SQL para usuario {current_user.id}: {request.question}")
        result = service.generate_sql(request)
        
        # Calcular tiempo de procesamiento
        processing_time = time.time() - start_time
        
        # Generar título automáticamente
        title = generate_title(request.question)
        
        # Convertir medical_terms a lista si es necesario
        medical_terms_list = None
        if request.medical_terms:
            # Asumir que medical_terms puede ser una lista de objetos o strings
            if isinstance(request.medical_terms, list):
                if request.medical_terms and isinstance(request.medical_terms[0], dict):
                    # Si son objetos con términos, extraer los términos
                    medical_terms_list = [term.get('term', str(term)) for term in request.medical_terms]
                else:
                    # Si ya son strings
                    medical_terms_list = [str(term) for term in request.medical_terms]
        
        # Registrar la consulta completa en el log del usuario
        query_log = QueryLog(
            user_id=current_user.id,
            title=title,
            question=request.question,
            medical_terms=medical_terms_list,
            generated_sql=result.generated_sql,
            is_executable=result.is_executable,
            attempts_count=result.attempts_count,
            error_message=result.error_message,
            processing_time=processing_time,
        )
        
        db.add(query_log)
        db.commit()
        db.refresh(query_log)
        
        # Log del resultado
        if result.is_executable:
            logger.info(f"SQL generado exitosamente en {result.attempts_count} intentos, tiempo: {processing_time:.2f}s")
        else:
            logger.warning(f"SQL no ejecutable después de {result.attempts_count} intentos: {result.error_message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generando SQL: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno generando SQL: {str(e)}"
        )

@router.get("/health")
def health_check(service: SQLGenerationService = Depends(get_sql_service)):
    """
    Verificar el estado del servicio de generación SQL.
    
    No requiere autenticación para facilitar monitoreo.
    """
    try:
        # Verificar que el servicio esté disponible
        if service is None:
            return {
                "status": "unhealthy",
                "service": "sql_generation",
                "error": "Service not initialized"
            }
        
        return {
            "status": "healthy",
            "service": "sql_generation",
            "model": service.model_name if hasattr(service, 'model_name') else "unknown"
        }
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "service": "sql_generation",
            "error": str(e)
        }